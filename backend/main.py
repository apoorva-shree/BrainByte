from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Perishable Food Optimizer API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "food_optimizer")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]
items_collection = db["items"]

# Pydantic Models
class FoodItemCreate(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str = "units"
    expiryDate: str
    location: str = "Not specified"

class FoodItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiryDate: Optional[str] = None
    location: Optional[str] = None
    consumed: Optional[bool] = None

class FoodItemResponse(BaseModel):
    id: str
    name: str
    category: str
    quantity: float
    unit: str
    expiryDate: str
    location: str
    addedDate: str
    consumed: bool
    daysUntilExpiry: int
    status: str

# Helper Functions
def calculate_days_until_expiry(expiry_date: str) -> int:
    try:
        expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        today = datetime.now()
        diff = expiry - today
        return diff.days
    except:
        return 0

def get_expiry_status(days_until_expiry: int) -> str:
    if days_until_expiry < 0:
        return "expired"
    elif days_until_expiry <= 2:
        return "critical"
    elif days_until_expiry <= 5:
        return "warning"
    else:
        return "good"

def format_item(item: dict) -> dict:
    days = calculate_days_until_expiry(item["expiryDate"])
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "category": item["category"],
        "quantity": item["quantity"],
        "unit": item["unit"],
        "expiryDate": item["expiryDate"],
        "location": item["location"],
        "addedDate": item["addedDate"],
        "consumed": item.get("consumed", False),
        "daysUntilExpiry": days,
        "status": get_expiry_status(days)
    }

# API Routes
@app.get("/api/health")
async def health_check():
    return {
        "success": True,
        "message": "FastAPI server is running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/items")
async def get_all_items():
    try:
        items = await items_collection.find().to_list(1000)
        formatted_items = [format_item(item) for item in items]
        return {"success": True, "items": formatted_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/items/{item_id}")
async def get_item(item_id: str):
    try:
        from bson import ObjectId
        item = await items_collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"success": True, "item": format_item(item)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: FoodItemCreate):
    try:
        from bson import ObjectId
        new_item = {
            "_id": ObjectId(),
            "name": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "unit": item.unit,
            "expiryDate": item.expiryDate,
            "location": item.location,
            "addedDate": datetime.now().isoformat(),
            "consumed": False
        }
        await items_collection.insert_one(new_item)
        return {"success": True, "item": format_item(new_item)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/items/{item_id}")
async def update_item(item_id: str, item: FoodItemUpdate):
    try:
        from bson import ObjectId
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        result = await items_collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": update_data},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"success": True, "item": format_item(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/items/{item_id}")
async def delete_item(item_id: str):
    try:
        from bson import ObjectId
        result = await items_collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"success": True, "message": "Item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/items/{item_id}/consume")
async def consume_item(item_id: str):
    try:
        from bson import ObjectId
        result = await items_collection.find_one_and_update(
            {"_id": ObjectId(item_id)},
            {"$set": {"consumed": True, "consumedDate": datetime.now().isoformat()}},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"success": True, "item": format_item(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/expiring/{days}")
async def get_expiring_items(days: int = 7):
    try:
        items = await items_collection.find({"consumed": False}).to_list(1000)
        expiring_items = []
        
        for item in items:
            days_left = calculate_days_until_expiry(item["expiryDate"])
            if 0 <= days_left <= days:
                expiring_items.append(format_item(item))
        
        expiring_items.sort(key=lambda x: x["daysUntilExpiry"])
        return {"success": True, "items": expiring_items, "count": len(expiring_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    try:
        items = await items_collection.find({"consumed": False}).to_list(1000)
        
        stats = {
            "total": len(items),
            "expired": 0,
            "critical": 0,
            "warning": 0,
            "good": 0,
            "consumed": await items_collection.count_documents({"consumed": True}),
            "categories": {}
        }
        
        for item in items:
            days = calculate_days_until_expiry(item["expiryDate"])
            status = get_expiry_status(days)
            stats[status] += 1
            
            category = item["category"]
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/category/{category}")
async def get_items_by_category(category: str):
    try:
        items = await items_collection.find({
            "category": {"$regex": f"^{category}$", "$options": "i"},
            "consumed": False
        }).to_list(1000)
        
        formatted_items = [format_item(item) for item in items]
        return {"success": True, "items": formatted_items, "count": len(formatted_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_items(query: str):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
        
        items = await items_collection.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}}
            ]
        }).to_list(1000)
        
        formatted_items = [format_item(item) for item in items]
        return {"success": True, "items": formatted_items, "count": len(formatted_items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
