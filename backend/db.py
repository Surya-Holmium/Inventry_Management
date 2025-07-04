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


class ComboBoxOptions(Base):
    __tablename__ = "ComboBoxOptions"
    option_id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=True)
    location = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    unit = Column(String, nullable=True)


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
            status="Active"
        ))
    if not db.query(InventoryItems).first():
        db.add(InventoryItems(
            item_id = "SKU0001",
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

    if not db.query(ComboBoxOptions).first():
        db.add(ComboBoxOptions(
            category = "Electronics",
            location = "Rack A",
            supplier = "ABC Components Pvt. Ltd.",
            unit = "pcs"
        ))

    if not db.query(TransactionsLogs).first():
        db.add(TransactionsLogs(
            transaction_id = "TL0001",
            item_id = "SKU0001",
            transaction_type = "Issuance",
            quantity = 1,
            issued_by = "Surya",
            issued_to = "Fayaz",
            issued_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
