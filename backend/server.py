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
from backend import get_db, Authentication, InventoryItems, ComboBoxOptions, TransactionsLogs

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
            return {"role": cred_db.role}
        else:
            return HTTPException(status_code=404, detail="User not found")
    except AttributeError as e:
        print(e)

# -------------------- Users ---------------------------------------
@app.get("/view_user")
@redis_cache(ttl=10)  
async def view_users(request: Request, db: Session = Depends(get_db)):
    try:
        result = []
        view_users = db.query(Authentication).all()
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
        # print(data)
        user_id = generate_next_id("new_user", db)
        db.add(Authentication(
            user_id = user_id,
            user_name= data["uName"],
            email= data["uEmail"],
            password=pwd_context.hash(data["uPwd"]),
            role= data["uRole"],
            status= "Active"
        ))
        db.commit()
        db.close()
        checkDB = db.query(Authentication).filter(Authentication.user_name == data["uName"]).first()
        if checkDB:
            print(checkDB.user_name)
            send_email_background.delay(data["uName"], data["uEmail"], data["uPwd"])
            return {"msg": True}
    except Exception as e:
        print(e)

@app.put("/update_user/{user_id}")
async def update_user(user_id: str, request: Request, db: Session=Depends(get_db)):
    print("hidfdjbndjvnbjd")
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
        view_items = db.query(InventoryItems).all()
        # return {"id": view_item.item_id, "item_name":view_item.item_name,}
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
            updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
        # Validate column name to prevent SQL injection
        valid_columns = [column.name for column in inspect(ComboBoxOptions).columns]
        if oType not in valid_columns:
            raise HTTPException(status_code=400, detail="Invalid column name")

        # Efficiently query only that column
        results = db.query(getattr(ComboBoxOptions, oType)).distinct().all()

        # Flatten result list of tuples
        return [value[0] for value in results if value[0] is not None]

    except Exception as e:
        print("Error in view_options:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")
    
@app.post("/options/{oType}")
async def add_options(oType: str, request: Request, db: Session = Depends(get_db)):
    try:
        print(oType)
        data = await request.json()
        if(oType == "category"):
            db.add(ComboBoxOptions(
                category = data["value"]
            ))
        elif(oType == "location"):
            db.add(ComboBoxOptions(
                location = data["value"]
            ))
        elif(oType == "supplier"):
            db.add(ComboBoxOptions(
                supplier = data["value"]
            ))
        else:
            db.add(ComboBoxOptions(
                unit = data["value"]
            ))
        db.commit()
        db.close()
        return {"msg": "option added successfully"}
    except Exception as e:
        print("Error in add_options:", e)
        return []

@app.get("/{itemOrEmpl}")
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
@app.post("/issue_stock")
async def issue_stock(request: Request, db: Session=Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        trans_id = generate_next_id("new_trans", db)
        is_item_name = db.query(InventoryItems).filter(InventoryItems.item_name == data["itemName"]).first()

        if not is_item_name:
            raise HTTPException(status_code=400, detail="Invalid column name")
        
        is_item_name.quantity = is_item_name.quantity - data.get("quantity", is_item_name.quantity)

        db.add(TransactionsLogs(
            transaction_id= trans_id,
            item_id=is_item_name.item_id,
            transaction_type="Issuance",
            quantity=data["quantity"],
            issued_by=data["issued_by"],
            issued_to=data["issued_to"],
            issued_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        db.commit()
        db.close()
    except Exception as e:
        print("Error in issue_stock:", e)
        raise HTTPException(status_code=400, detail="Invalid column name")


# ----------------------------------------------Helper function--------------------------------------------
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