from motor.motor_asyncio import AsyncIOMotorClient
from config import Auth

mongo = AsyncIOMotorClient(Auth.mongo_auth)
db = mongo["kp_p"]


async def set(collection, _id, data):
    i = {"_id": _id}
    if await db[collection].count_documents({"_id": _id}) == 0:
        await db[collection].insert_one({**i, **data})
    else:
        await db[collection].update_one(i, {"$set": data})
