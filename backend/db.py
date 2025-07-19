from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import quote_plus
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

encoded_password = quote_plus(os.getenv("DB_PASSWORD"))

# 1. Connect to default postgres DB to check if Inventory_Management exists
def create_database_if_not_exists():
    try:
        con = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port="5432"
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Required to CREATE DATABASE
        cur = con.cursor()

        # Check if DB exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (os.getenv("DB_NAME"),))
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE \"{os.getenv("DB_NAME")}\"")
            print(f"✅ Database '{os.getenv("DB_NAME")}' created successfully.")
        else:
            print(f"ℹ️ Database '{os.getenv("DB_NAME")}' already exists.")
        cur.close()
        con.close()

    except Exception as e:
        print(f"❌ Error creating database: {e}")

# 2. Now connect to your actual app DB
DATABASE_URL = f"postgresql://{os.getenv("DB_USER")}:{encoded_password}@localhost:5432/{os.getenv("DB_NAME")}"

create_database_if_not_exists()  # Call this before using SQLAlchemy

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Authentication(Base):
    __tablename__ = "Authentication"
    index = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False)
    user_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False)


class InventoryItems(Base):
    __tablename__ = "Inventory"
    index = Column(Integer, primary_key=True, index=True)
    item_id = Column(String, unique=True, nullable=False)
    item_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    supplier = Column(String, nullable=False)
    location = Column(String, nullable=False)
    min_stock = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


# class Subcategory(Base):
#     __tablename__ = "subcategories"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

#     __table_args__ = (UniqueConstraint("name", "category_id", name="_subcategory_uc"),)


class TempHandleEditStock(Base):
    __tablename__ = "tempHandleEditStock"
    id = Column(Integer, primary_key=True, index=True)
    itemname = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=True)
    supplier = Column(String, nullable=True)
    status = Column(String, nullable=False)


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class TransactionsLogs(Base):
    __tablename__ = "TransactionsLogs"
    index = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False)
    item_id = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    issued_by = Column(String, nullable=False)
    issued_to = Column(String, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)  # Creates tables

    db = SessionLocal()
    if not db.query(Authentication).first():
        db.add(Authentication(
            user_id ="E0001",
            user_name="Surya",
            email="dev2.holmium@gmail.com",
            password=pwd_context.hash("sUrya@839"),
            role="Admin",
            status="Inactive"
        ))
    if not db.query(InventoryItems).first():
        db.add(InventoryItems(
            item_id = "SKU0001",
            item_name = "Electrolyte Capacitors",
            category = "Electronics",
            description = "Electrolyte Cap 100uF/50V",
            quantity = 30,
            unit_price = 450.00,
            supplier = "ABC Components Pvt. Ltd.",
            location = "Store Room A",
            min_stock = 10,
            unit = "pcs",
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

    # if not db.query(Category).filter_by(name="Capacitors").first():
    #     category = Category(name="Capacitors")
    #     db.add(category)
    #     db.commit()  # So it gets an ID
    #     db.refresh(category)  # Refresh to access generated ID
    # else:
    #     category = db.query(Category).filter_by(name="Capacitors").first()
    
    # if not db.query(Subcategory).filter_by(name="Ceramic Capacitors", category_id=category.id).first():
    #     db.add(Subcategory(
    #         name="Ceramic Capacitors",
    #         category_id=category.id
    #     ))

    if not db.query(Category).first():
        db.add(Category(
            name = "Capacitors"
        ))

    if not db.query(TempHandleEditStock).first():
        db.add(TempHandleEditStock(
            itemname = "Electrolyte Capacitors",
            quantity = 100,
            unit_price = None,
            supplier = None,
            status = "Pending"
        ))

    if not db.query(Supplier).first():
        db.add(Supplier(
            name = "SIMCOM",
        ))

    if not db.query(Location).first():
        db.add(Location(
            name = "Rack A",
        ))

    if not db.query(Unit).first():
        db.add(Unit(
            name = "pcs",
        ))

    if not db.query(TransactionsLogs).first():
        db.add(TransactionsLogs(
            transaction_id = "TL0001",
            item_id = "SKU0001",
            transaction_type = "Issuance",
            quantity = 1,
            issued_by = "Surya",
            issued_to = "Fayaz",
            issued_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status = "Pending"
        ))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
