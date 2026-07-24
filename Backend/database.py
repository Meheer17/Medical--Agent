import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument, IndexModel, ASCENDING
from config import settings

class MongoDBManager:
    client: AsyncIOMotorClient = None
    db = None

db_manager = MongoDBManager()

def get_db():
    """Dependency to get MongoDB database instance"""
    return db_manager.db

async def connect_to_mongo():
    """Initialize MongoDB connection client"""
    db_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_manager.db = db_manager.client[settings.DATABASE_NAME]
    print(f"Connected to MongoDB at {settings.MONGODB_URL}/{settings.DATABASE_NAME}")

async def close_mongo_connection():
    """Close MongoDB connection client"""
    if db_manager.client:
        db_manager.client.close()
        print("Closed MongoDB connection.")

async def get_next_sequence_value(sequence_name: str) -> int:
    """
    Atomically generates sequential integer IDs for collections
    to preserve integer ID compatibility with the Android frontend.
    """
    db = get_db()
    result = await db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return result["seq"]

async def init_db():
    """Create database indexes on MongoDB startup"""
    await connect_to_mongo()
    db = get_db()

    # Users collection indexes
    await db.users.create_index("id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.users.create_index("doctor_code", sparse=True)
    await db.users.create_index("role")

    # Doctor Appointments indexes
    await db.doctor_appointments.create_index("id", unique=True)
    await db.doctor_appointments.create_index("patient_id")
    await db.doctor_appointments.create_index("doctor_id")

    # Lab Appointments indexes
    await db.lab_appointments.create_index("id", unique=True)
    await db.lab_appointments.create_index("patient_id")
    await db.lab_appointments.create_index("lab_id")

    # Lab Reports indexes
    await db.lab_reports.create_index("id", unique=True)
    await db.lab_reports.create_index("appointment_id", unique=True)
    await db.lab_reports.create_index("uploaded_by_id")

    # Queries indexes
    await db.queries.create_index("id", unique=True)
    await db.queries.create_index("patient_id")
    await db.queries.create_index("doctor_id")
