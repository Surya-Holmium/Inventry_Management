from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from passlib.context import CryptContext
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DB_NAME = "Inventory_Management"
DB_USER = "postgres"
DB_PASSWORD = "sUrya@839"
DB_HOST = "localhost"
DB_PORT = "5432"

# 1. Connect to default postgres DB to check if Inventory_Management exists
def create_database_if_not_exists():
    try:
        con = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Required to CREATE DATABASE
        cur = con.cursor()

        # Check if DB exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_NAME,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE \"{DB_NAME}\"")
            print(f"✅ Database '{DB_NAME}' created successfully.")
        else:
            print(f"ℹ️ Database '{DB_NAME}' already exists.")
        cur.close()
        con.close()

    except Exception as e:
        print(f"❌ Error creating database: {e}")

# 2. Now connect to your actual app DB
DATABASE_URL = DATABASE_URL = f"postgresql://postgres:sUrya%40839@localhost:5432/{DB_NAME}"

create_database_if_not_exists()  # Call this before using SQLAlchemy

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Authentication(Base):
    __tablename__ = "Authentication"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False)

class InventoryItems(Base):
    __tablename__ = "Inventory"
    item_id = Column(Integer, primary_key=True, index=True)
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
            user_name="Surya",
            email="dev2.holmium@gmail.com",
            password=pwd_context.hash("sUrya@839"),
            role="Admin",
            status="Active"
        ))
    if not db.query(InventoryItems).first():
        db.add(InventoryItems(
            item_name = "Motor Controller",
            category = "Electronics",
            description = "24V DC 30A motor controller",
            quantity = 30,
            unit_price = 450.00,
            supplier = "ABC Components Pvt. Ltd.",
            location = "Store Room A",
            min_stock = 10,
            unit = "pcs",
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
