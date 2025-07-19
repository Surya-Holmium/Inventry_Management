from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from contextlib import asynccontextmanager
from tasks import send_email_background
import uvicorn
import sys, os, functools, json
from dotenv import load_dotenv
from datetime import datetime
import uvicorn
import redis.asyncio as redis
from passlib.context import CryptContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import get_db, Authentication, InventoryItems, Category, TransactionsLogs, Location, Supplier, Unit, TempHandleEditStock

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- app startup / shutdown --------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI Server Starting...")
    app.state.redis = redis.from_url(
        f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/2",
        encoding="utf-8",
        decode_responses=True
    )
    yield
    print("🛑 FastAPI Server Shutting Down Gracefully...")

app = FastAPI(lifespan=lifespan)


# ---------- tiny Redis‑cache decorator ----------------------------
def redis_cache(ttl: int = 5):
    def deco(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kw):
            req: Request = kw.get("request")
            redis = req.app.state.redis          # set in lifespan()
            key   = f"{fn.__name__}:{args}:{kw}"
            if data := await redis.get(key):
                return json.loads(data)
            result = await fn(*args, **kw)
            await redis.set(key, json.dumps(result), ex=ttl)
            return result
        return wrapper
    return deco

# -------------------- Auth ----------------------------------------
@app.post("/login")
async def handle_login(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        username = data["user"]
        password = data["pass"]
        cred_db = db.query(Authentication).filter(Authentication.user_name == username).first()
        if cred_db.user_name == username and pwd_context.verify(password, cred_db.password):
            if cred_db.status == "Inactive":
                cred_db.status = "Active"
            db.commit()
            if cred_db.status == "Active":
                return {"role": cred_db.role}
        else:
            return HTTPException(status_code=404, detail="User not found")
    except AttributeError as e:
        print(e)

@app.post("/logout/{userName}")
async def logout_user(userName: str, request: Request, db: Session=Depends(get_db)):
    try:
        data = await request.json()
        if data["msg"]:
            view_user = db.query(Authentication).filter(Authentication.user_name == userName).first()
            if view_user.status == "Active":
                view_user.status = "Inactive"
        db.commit()
        if view_user.status == "Inactive":
            return {"msg": True}
    except Exception as e:
        print("Error in logout_users:", e)
        raise HTTPException(status_code=400, detail="Invalid user name")

# -------------------- Users ---------------------------------------
@app.get("/view_user")
@redis_cache(ttl=10)  
async def view_users(request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        view_users = db.query(Authentication).order_by(Authentication.user_id).all()
        for view_user in view_users:
            result.append({
                "user_id": view_user.user_id,
                "uName": view_user.user_name, 
                "uEmail":view_user.email, 
                "uRole": view_user.role, 
                "sts": view_user.status
            })
        return result
    except Exception as e:
        print(e)

@app.post("/add_user")
async def add_user(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        user_id = generate_next_id("new_user", db)
        db.add(Authentication(
            user_id = user_id,
            user_name= data["uName"],
            email= data["uEmail"],
            password=pwd_context.hash(data["uPwd"]),
            role= data["uRole"],
            status= "Inactive"
        ))
        db.commit()
        checkDB = db.query(Authentication).filter(Authentication.user_name == data["uName"]).first()
        if checkDB:
            print(checkDB.user_name)
            send_email_background.delay(data["uName"], data["uEmail"], data["uPwd"])
            return {"msg": True}
    except Exception as e:
        print(e)

@app.put("/update_user/{user_id}")
async def update_user(user_id: str, request: Request, db: Session=Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        # Fetch item by ID
        user = db.query(Authentication).filter(Authentication.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields
        user.user_name = data.get("uName", user.user_name)
        user.email = data.get("uEmail", user.email)
        user.password = data.get("uPwd", user.password)
        user.role = data.get("uRole", user.role)

        db.commit()
        db.close()
        return {"msg": "User updated successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: str, db: Session=Depends(get_db)):
    user = db.query(Authentication).filter(Authentication.user_id == user_id).first()
    print(user.user_name)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(user)
    db.commit()
    return {"msg": "User deleted"}


# -------------------- Inventory -----------------------------------
@app.get("/view_inventory")
@redis_cache(ttl=10)  
async def view_inventory(request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        view_items = db.query(InventoryItems).order_by(InventoryItems.item_id).all()
        for view_item in view_items:
            result.append({
                "id": view_item.item_id, 
                "item_name":view_item.item_name, 
                "category": view_item.category, 
                "description": view_item.description, 
                "quantity": view_item.quantity, 
                "unit_price": view_item.unit_price, 
                "supplier": view_item.supplier, 
                "location": view_item.location, 
                "min_stock": view_item.min_stock, 
                "unit": view_item.unit, 
                "created_at": view_item.created_at.isoformat() if view_item.created_at else None,
                "updated_at": view_item.updated_at.isoformat() if view_item.updated_at else None,
            })
        return result

    except Exception as e:
        print(e)


@app.post("/create_new_item")
async def add_stock(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        item_id = generate_next_id("new_item",db)
        db.add(InventoryItems(
            item_id = item_id,
            item_name=data["itemName"],
            category=data["category"],
            description=data["description"],
            quantity=data["quantity"],
            unit_price=data["unitPrice"],
            supplier=data["supplier"],
            location=data["location"],
            min_stock=data["minStock"],
            unit=data["unit"],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.commit()
        db.close()
        return {"msg": True}
    except Exception as e:
        print(e)

@app.put("/update_value/{item_id}")
async def update_value(item_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        # Fetch item by ID
        item = db.query(InventoryItems).filter(InventoryItems.item_id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update fields
        item.quantity = item.quantity + data.get("quantity", item.quantity)
        item.unit_price = data.get("unitPrice", item.unit_price)
        item.supplier = data.get("supplier", item.supplier)
        item.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.commit()
        db.close()
        return {"msg": "Item updated successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.delete("/delete_item/{item_id}")
async def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(InventoryItems).filter(InventoryItems.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"msg": "Item deleted"}

# -------------------- Options -------------------------------------
@app.get("/options/{oType}")
async def view_options(oType: str, db: Session = Depends(get_db)):
    try:
        if(oType == "category"):
            results = db.query(Category).all()
        elif(oType == "location"):
            results = db.query(Location).all()
        elif (oType == "supplier"):
            results = db.query(Supplier).all()
        else:
            results = db.query(Unit).all()
        return [value.name for value in results if value.name is not None]

    except Exception as e:
        print("Error in view_options:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")
    
@app.post("/options/{oType}")
async def add_options(oType: str, request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        if(oType == "category"):
            db.add(Category(
                name = data["value"]
            ))
        elif(oType == "location"):
            db.add(Location(
                name = data["value"]
            ))
        elif(oType == "supplier"):
            db.add(Supplier(
                name = data["value"]
            ))
        else:
            db.add(Unit(
                name = data["value"]
            ))
        db.commit()
        db.close()
        return {"msg": "option added successfully"}
    except Exception as e:
        print("Error in add_options:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")
    
# @app.get("/subcategory/{category}")
# async def view_subcategory(category: str, db: Session = Depends(get_db)):
#     try:
#         category = db.query(Category).filter_by(name=category).first()
#         if not category:
#             raise HTTPException(status_code=404, detail="Category not found")

#         subcategories = db.query(Subcategory).filter_by(category_id=category.id).all()

#         return [sub.name for sub in subcategories if sub.name]
#     except Exception as e:
#         print("Error in view_subcategory:", e)
#         raise HTTPException(status_code=500, detail="Internal server error")

# @app.post("/subcategory/{subCat}")
# async def add_subcategory(subCat: str, request: Request, db: Session = Depends(get_db)):
#     try:
        
#     except Exception as e:
#         print("Error in view_subcategory:", e)
#         raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/employee/{itemOrEmpl}")
async def view_itemOrEmpl(itemOrEmpl: str, db: Session = Depends(get_db)):
    try:
        if itemOrEmpl == "item_name":
            results = db.query(getattr(InventoryItems, itemOrEmpl)).distinct().all()
        elif itemOrEmpl == "issued_by" or itemOrEmpl == "issued_to":
            results = db.query(getattr(Authentication, "user_name")).distinct().all()
        
        return [value[0] for value in results if value[0] is not None]

    except Exception as e:
        print("Error in view_itemOrEmpl:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")

# -------------------- Issue stock ---------------------------------
@app.post("/issue_stock/{role}")
async def issue_stock(role: str, request: Request, db: Session=Depends(get_db)):
    try:
        data = await request.json()
        issued_stock_through(data, db, role)
    except Exception as e:
        print("Error in issue_stock:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")

# ---------------------------------------------Raise and Manage Request------------------------------------
@app.get("/requests/{stockIn_stockOut}")
@redis_cache(ttl=10)  
async def view_requests(stockIn_stockOut:str, request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        if stockIn_stockOut == "stock_in":
            results = db.query(TempHandleEditStock).filter(TempHandleEditStock.status == "Pending").all()
            for value in results:
                result.append({
                    "itemName": value.itemname, 
                    "quantity":value.quantity, 
                    "uPrice": value.unit_price, 
                    "supplier": value.supplier,
                    "sts": value.status
                })
        else:
            results = db.query(TransactionsLogs).filter(TransactionsLogs.status == "Pending").all()
            for value in results:
                itemName = db.query(InventoryItems).filter(InventoryItems.item_id == value.item_id).first().item_name
                result.append({
                    "tran_id": value.transaction_id,
                    "item_id": value.item_id,
                    "itemName": itemName,
                    "quantity": value.quantity,
                    "issued_by": value.issued_by,
                    "issued_to": value.issued_to,
                    "issued_at": value.issued_at.isoformat() if value.issued_at else None,
                    "sts": value.status
                })
        return result
    except Exception as e:
        print("Error in view_request:", e)
        raise HTTPException(status_code=400, detail="Requests not founud")
    
@app.post("/accept_request/{stockIn_stockOut}")
async def accept_request(stockIn_stockOut: str, request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        if stockIn_stockOut == "stock_in":
            if data:
                view_item = db.query(InventoryItems).filter(InventoryItems.item_name == data["itemName"]).first()
                view_item.quantity = view_item.quantity + data.get("quantity", view_item.quantity)
                if data["unitPrice"] is not None:
                    view_item.unit_price = data.get("unitPrice", view_item.unit_price)

                if data["supplier"] != "":
                    view_item.supplier = data.get("supplier", view_item.supplier)
                view_item.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = db.query(TempHandleEditStock).filter(TempHandleEditStock.status == "Pending").first()
                result.status = "Approved"
            db.commit()
            db.close()
            return {"msg": "Stock in request updated successfully!"}
        else:
            if data:
                view_item = db.query(InventoryItems).filter(InventoryItems.item_id == data["item_id"]).first()
                view_item.quantity = view_item.quantity - data.get("quantity", view_item.quantity)
                view_item.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                result = db.query(TransactionsLogs).filter(TransactionsLogs.status == "Pending").first()
                result.status = "Approved"
            db.commit()
            db.close()
            return {"msg": "Stock out request updated successfully!"}
    except Exception as e:
        print("Error in view_request:", e)
        raise HTTPException(status_code=400, detail="Requests not founud")
    
@app.delete("/reject_request/{stockIn_stockOut}/{itemName}")
async def reject_request(stockIn_stockOut: str, itemName: str, db: Session = Depends(get_db)):
    try:
        if stockIn_stockOut == "stock_in":
            result = db.query(TempHandleEditStock).filter(TempHandleEditStock.itemname == itemName).first()
            if not result:
                raise HTTPException(status_code=404, detail="Item not found")
            db.delete(result)    
            db.commit()
            db.close()
            return {"msg": "Request rejected successfully!"}
        else:
            itemID = db.query(InventoryItems).filter(InventoryItems.item_name == itemName).first().item_id
            result = db.query(TransactionsLogs).filter(TransactionsLogs.item_id == itemID).first()
            if not result:
                raise HTTPException(status_code=404, detail="Item not found")
            db.delete(result)    
            db.commit()
            db.close()
            return {"msg": "Request rejected successfully!"}
                
    except Exception as e:
        print("Error in reject_request:", e)
        raise HTTPException(status_code=400, detail="Requests not founud")

@app.post("/raise_request/{stockIn_stockOut}")
async def raise_request(stockIn_stockOut: str, request: Request, db: Session=Depends(get_db)):
    try:
        data = await request.json()
        if stockIn_stockOut == "stock_in":
            view_item = db.query(InventoryItems).filter(InventoryItems.item_name == data["itemName"]).first()
            db.add(TempHandleEditStock(
                itemname=data["itemName"],
                quantity=data["quantity"],
                unit_price=data["unitPrice"] if view_item.unit_price != data["unitPrice"] else None,
                supplier=data["supplier"] if view_item.supplier != data["supplier"] else None,
                status="Pending"
            ))
            db.commit()
            db.close()
        else:
            issued_stock_through(data, db, "Store Operator")
    except Exception as e:
        print("Error in raise_request:", e)
        raise HTTPException(status_code=400, detail="Item not founud")

# ----------------------------------------------Helper function--------------------------------------------
def issued_stock_through(data, db:Session, role):
    trans_id = generate_next_id("new_trans", db)
    is_item_name = db.query(InventoryItems).filter(InventoryItems.item_name == data["itemName"]).first()

    if not is_item_name:
        raise HTTPException(status_code=400, detail="Invalid column name")

    db.add(TransactionsLogs(
        transaction_id= trans_id,
        item_id=is_item_name.item_id,
        transaction_type="Issuance",
        quantity=data["quantity"],
        issued_by=data["issued_by"],
        issued_to=data["issued_to"],
        issued_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="Approved" if (role == "Admin" or role == "Manager") else "Pending"
    ))

    db.commit()
    db.close()

def generate_next_id(creation_type: str, db: Session) -> str:
    if creation_type == "new_item":
        latest = db.query(InventoryItems).order_by(InventoryItems.index.desc()).first()
        prefix = "SKU"
        field  = "item_id"
    elif creation_type == "new_user":
        latest = db.query(Authentication).order_by(Authentication.index.desc()).first()
        prefix = "E"
        field  = "user_id"
    else:                       # new_trans
        latest = db.query(TransactionsLogs).order_by(TransactionsLogs.index.desc()).first()
        prefix = "TL"
        field  = "transaction_id"

    if not latest:
        return f"{prefix}0001"

    last_num = int(getattr(latest, field)[len(prefix):])
    return f"{prefix}{last_num + 1:04d}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)