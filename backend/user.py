from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # default local MongoDB
db = client["food_detection"]  # database
users_collection = db["users"]  # collection

# Create a user document
user_doc = {
    "username": "jasmin123",
    "email": "jasmin@example.com",
    "created_at": datetime(2026, 2, 8, 0, 0)
}

# Insert into MongoDB
result = users_collection.insert_one(user_doc)
print("Inserted user with ID:", result.inserted_id)
