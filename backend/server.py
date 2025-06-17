from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import uvicorn
import sys
import os
import uvicorn
from passlib.context import CryptContext
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend import get_db, Authentication, InventoryItems

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

@app.get("/view_in")
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)