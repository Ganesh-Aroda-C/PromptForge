import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import motor.motor_asyncio
from backend.app.core.config import settings

logger = logging.getLogger("promptforge.database")

class LocalJsonCollection:
    """
    High-performance, persistent JSON collection providing an async interface
    identical to Motor/MongoDB collections. Enables seamless local development
    and fallback when MongoDB daemon is not running.
    """
    def __init__(self, name: str, storage_dir: str):
        self.name = name
        self.filepath = os.path.join(storage_dir, f"{name}.json")
        self._lock = asyncio.Lock()
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_sync(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_sync(self, data: List[Dict[str, Any]]):
        temp_file = f"{self.filepath}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(temp_file, self.filepath)

    async def find(self, filter_query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            docs = self._read_sync()
            
            if filter_query:
                filtered = []
                for doc in docs:
                    match = True
                    for k, v in filter_query.items():
                        if k.startswith("$"):
                            continue
                        if doc.get(k) != v:
                            match = False
                            break
                    if match:
                        filtered.append(doc)
                docs = filtered

            if sort:
                for field, direction in reversed(sort):
                    docs.sort(key=lambda x: str(x.get(field, "")), reverse=(direction == -1))

            if limit:
                docs = docs[:limit]

            return docs

    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        results = await self.find(filter_query, limit=1)
        return results[0] if results else None

    async def insert_one(self, document: Dict[str, Any]):
        async with self._lock:
            docs = self._read_sync()
            doc_copy = dict(document)
            if "created_at" not in doc_copy:
                doc_copy["created_at"] = datetime.utcnow().isoformat()
            docs.append(doc_copy)
            self._write_sync(docs)
            return type("InsertResult", (), {"inserted_id": doc_copy.get("_id", doc_copy.get("id"))})()

    async def update_one(self, filter_query: Dict[str, Any], update_doc: Dict[str, Any]):
        async with self._lock:
            docs = self._read_sync()
            matched = False
            for doc in docs:
                match = True
                for k, v in filter_query.items():
                    if doc.get(k) != v:
                        match = False
                        break
                if match:
                    if "$set" in update_doc:
                        for k, v in update_doc["$set"].items():
                            doc[k] = v
                    else:
                        for k, v in update_doc.items():
                            doc[k] = v
                    doc["updated_at"] = datetime.utcnow().isoformat()
                    matched = True
                    break
            if matched:
                self._write_sync(docs)
            return type("UpdateResult", (), {"matched_count": 1 if matched else 0})()

    async def delete_one(self, filter_query: Dict[str, Any]):
        async with self._lock:
            docs = self._read_sync()
            initial_len = len(docs)
            docs = [d for d in docs if not all(d.get(k) == v for k, v in filter_query.items())]
            if len(docs) < initial_len:
                self._write_sync(docs)
            return type("DeleteResult", (), {"deleted_count": initial_len - len(docs)})()

    async def count_documents(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        res = await self.find(filter_query)
        return len(res)


class DatabaseManager:
    def __init__(self):
        self.is_mongodb_connected = False
        self.mongo_client = None
        self.db = None
        self.storage_dir = settings.STORAGE_DIR
        self.collections: Dict[str, Any] = {}

    async def connect(self):
        """Test MongoDB connection or gracefully fall back to local storage."""
        try:
            self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=1500
            )
            # Ping database
            await self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[settings.DATABASE_NAME]
            self.is_mongodb_connected = True
            logger.info("Successfully connected to live MongoDB server.")
        except Exception as e:
            self.is_mongodb_connected = False
            logger.warning(f"MongoDB not available ({e}). Using persistent LocalJsonStorage engine.")

    def get_collection(self, collection_name: str):
        if self.is_mongodb_connected and self.db is not None:
            return self.db[collection_name]
        
        if collection_name not in self.collections:
            self.collections[collection_name] = LocalJsonCollection(collection_name, self.storage_dir)
        return self.collections[collection_name]

db_manager = DatabaseManager()

def get_db(collection_name: str):
    return db_manager.get_collection(collection_name)
