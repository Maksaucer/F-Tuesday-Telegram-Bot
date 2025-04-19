# database/__init__.py
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

_db_pool = None

async def init_db():
    global _db_pool
    if _db_pool is None:
        try:
            _db_pool = await asyncpg.create_pool(DATABASE_URL)
            print("Database connection pool initialized successfully.")
        except Exception as e:
            print(f"Failed to initialize database pool: {e}")
            _db_pool = None

def get_db_pool():
    if _db_pool is None:
        raise RuntimeError("Database pool has not been initialized. Call init_db() first.")
    return _db_pool