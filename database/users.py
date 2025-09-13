# database/users.py

from database import get_db_pool

async def get_username(user_id: int):
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool is not initialized.")
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT username FROM users WHERE telegram_id = $1
        """, user_id)
        return row["username"] if row else None

async def add_user(user_id: int, username: str = "UNIDENTIFIED"):
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool is not initialized.")
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, username, subscribed, filters)
            VALUES ($1, $2, TRUE, '{}')
            ON CONFLICT (telegram_id) DO UPDATE
            SET username = EXCLUDED.username,
                subscribed = TRUE,
                filters = COALESCE(users.filters, '{}')
        """, user_id, username)

async def unsubscribe_user(user_id: int):
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool is not initialized.")
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET subscribed = FALSE
            WHERE telegram_id = $1
        """, user_id)

async def remove_user(user_id: int):
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool is not initialized.")
    async with pool.acquire() as conn:
        await conn.execute("""
            DELETE FROM users WHERE telegram_id = $1
        """, user_id)

async def load_users():
    pool = get_db_pool()
    if pool is None:
        raise Exception("Database pool is not initialized.")
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT telegram_id FROM users
            WHERE subscribed = TRUE
        """)
        return [row["telegram_id"] for row in rows]