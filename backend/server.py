from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session, load_only
from sqlalchemy import inspect
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
from datetime import datetime
import uvicorn
from passlib.context import CryptContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import get_db, Authentication, InventoryItems, ComboBoxOptions

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI Server Starting...")
    yield
    print("🛑 FastAPI Server Shutting Down Gracefully...")

app = FastAPI(lifespan=lifespan)

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

@app.get("/view_inventory")
async def view_inventory(db: Session = Depends(get_db)):
    try:
        result = []
        view_items = db.query(InventoryItems).all()
        # return {"id": view_item.item_id, "item_name":view_item.item_name,}
        for view_item in view_items:
            result.append({"id": view_item.item_id, "item_name":view_item.item_name, "category": view_item.category, "description": view_item.description, "quantity": view_item.quantity, "unit_price": view_item.unit_price, "supplier": view_item.supplier, "location": view_item.location, "min_stock": view_item.min_stock, "unit": view_item.unit, "created_at": view_item.created_at, "updated_at": view_item.updated_at})
        return result

    except Exception as e:
        print(e)

@app.get("/view_user")
async def view_users(db: Session = Depends(get_db)):
    try:
        result = []
        view_items = db.query(Authentication).all()
        for view_item in view_items:
            result.append({
                "uName": view_item.user_name, 
                "uEmail":view_item.email, 
                "uRole": view_item.role, 
                "sts": view_item.status
            })
        return result

    except Exception as e:
        print(e)

@app.post("/add_user")
async def add_user(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        print(data)
        db.add(Authentication(
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
            return {"msg": True}
    except Exception as e:
        print(e)

@app.post("/create_new_item")
async def add_stock(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        item_id = generate_next_item_id(db)
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
        item.quantity = data.get("quantity", item.quantity)
        item.unit_price = data.get("unitPrice", item.unit_price)
        item.supplier = data.get("supplier", item.supplier)
        item.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.commit()
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
        return []
    
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
        elif(oType == "location"):
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

# ----------------------------------------------Helper function--------------------------------------------
def generate_next_item_id(db:Session):
    latest_item = (db.query(InventoryItems).order_by(InventoryItems.index.desc()).first())

    if not latest_item:
        return "SKU0001"
    
    last_num = int(latest_item.item_id[3:])
    next_num = last_num + 1
    return f"SKU{next_num:04d}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)