import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config


class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.DATABASE_NAME]
        self.users = self.db["users"]
        self.chats = self.db["chats"]
        self.apps = self.db["apps"]

    # ─── USER METHODS ───────────────────────────────────────────────────

    async def add_user(self, user_id: int):
        if not await self.is_user_exist(user_id):
            await self.users.insert_one({"id": user_id, "expiry_time": None})

    async def is_user_exist(self, user_id: int) -> bool:
        user = await self.users.find_one({"id": user_id})
        return bool(user)

    async def get_user(self, user_id: int):
        return await self.users.find_one({"id": user_id})

    async def update_user(self, data: dict):
        user_id = data["id"]
        if not await self.is_user_exist(user_id):
            await self.users.insert_one(data)
        else:
            await self.users.update_one({"id": user_id}, {"$set": data})

    async def total_users_count(self) -> int:
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id: int):
        await self.users.delete_one({"id": user_id})

    # ─── PREMIUM METHODS ────────────────────────────────────────────────

    async def is_premium(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user or not user.get("expiry_time"):
            return False
        expiry = user["expiry_time"]
        if expiry.tzinfo is None:
            expiry = pytz.utc.localize(expiry)
        return expiry > datetime.datetime.now(pytz.utc)

    async def remove_premium_access(self, user_id: int) -> bool:
        user = await self.get_user(user_id)
        if not user:
            return False
        await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return True

    # ─── CHAT METHODS ────────────────────────────────────────────────────

    async def add_chat(self, chat_id: int):
        if not await self.is_chat_exist(chat_id):
            await self.chats.insert_one({"id": chat_id})

    async def is_chat_exist(self, chat_id: int) -> bool:
        chat = await self.chats.find_one({"id": chat_id})
        return bool(chat)

    async def total_chat_count(self) -> int:
        return await self.chats.count_documents({})

    async def get_all_chats(self):
        return self.chats.find({})

    async def delete_chat(self, chat_id: int):
        await self.chats.delete_one({"id": chat_id})

    # ─── APP METHODS ─────────────────────────────────────────────────────

    async def add_app(self, user_id: int, url: str) -> bool:
        """Add an app URL for monitoring. Returns False if limit reached."""
        is_prem = await self.is_premium(user_id)
        existing = await self.get_user_apps(user_id)
        limit = None if is_prem else Config.FREE_USER_LIMIT
        if limit and len(existing) >= limit:
            return False
        # Avoid duplicates
        for app in existing:
            if app["url"] == url:
                return True
        await self.apps.insert_one({"user_id": user_id, "url": url, "status": "unknown"})
        return True

    async def remove_app(self, user_id: int, url: str):
        await self.apps.delete_one({"user_id": user_id, "url": url})

    async def get_user_apps(self, user_id: int) -> list:
        cursor = self.apps.find({"user_id": user_id})
        return await cursor.to_list(length=None)

    async def get_all_apps(self) -> list:
        cursor = self.apps.find({})
        return await cursor.to_list(length=None)

    async def update_app_status(self, user_id: int, url: str, status: str):
        await self.apps.update_one(
            {"user_id": user_id, "url": url},
            {"$set": {"status": status}}
        )

    async def total_apps_count(self) -> int:
        return await self.apps.count_documents({})


db = Database()
