import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import AsyncMongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncMongoClient(MONGO_URL)
db = client["appdb"]

app = FastAPI()

# Allow the browser (Next.js on :3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str

@app.get("/api/health")
async def health():
    await client.admin.command("ping")   # proves Mongo is reachable
    return {"status": "ok"}

@app.post("/api/items")
async def create_item(item: Item):
    result = await db.items.insert_one(item.model_dump())
    return {"id": str(result.inserted_id), "name": item.name}

@app.get("/api/items")
async def list_items():
    return [{"id": str(d["_id"]), "name": d["name"]} async for d in db.items.find()]