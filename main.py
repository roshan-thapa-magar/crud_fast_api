from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import motor.motor_asyncio
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(
    "mongodb+srv://roshanthapamagarmagar:xllaJ4rVljwx1Tni@cluster0.crqpre8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client.userdb  # database name
collection = db.users  # collection name

# Helper to convert MongoDB ObjectId to string
def serialize_user(user) -> dict:
    return {
        "_id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "password": user.get("password", "")
    }


# Request model
class User(BaseModel):
    name: str
    email: EmailStr
    password: str

# Response model
class UserOut(BaseModel):
    _id: str
    name: str
    email: EmailStr
    password: str

# ✅ POST: Create user
@app.post("/users", response_model=UserOut)
async def create_user(user: User):
    if await collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    result = await collection.insert_one(user.dict())
    created_user = await collection.find_one({"_id": result.inserted_id})
    return serialize_user(created_user)

# ✅ GET: Fetch all users
@app.get("/users", response_model=List[UserOut])
async def get_users():
    users = []
    async for user in collection.find():
        users.append(serialize_user(user))
    return users
    console.log(users)

# ✅ PUT: Update user by ID
@app.put("/users/{id}", response_model=UserOut)
async def update_user(id: str, updated: User):
    result = await collection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": updated.dict()},
        return_document=True
    )
    if result:
        return serialize_user(result)
    raise HTTPException(status_code=404, detail="User not found")

# ✅ DELETE: Delete user by ID
@app.delete("/users/{id}")
async def delete_user(id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")
