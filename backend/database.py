import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
foods_collection = db["foods"]
detections_collection = db["detections"]
inventory_collection = db["inventory_batches"]
routes_collection = db["routes"]
alerts_collection = db["alerts"]