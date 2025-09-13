# database/filters.py
from database import get_db_pool

# Получить список фильтров пользователя
async def get_filters(user_id: int) -> list[str]:
    pool = get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT filters FROM users WHERE telegram_id = $1
        """, user_id)
        return row["filters"] if row and row["filters"] else []

# Добавить фильтр, если его ещё нет
async def add_filter(user_id: int, tag: str):
    if not isinstance(tag, str):
        raise ValueError("Тег должен быть строкой")
        
    pool = get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET filters = ARRAY(
                SELECT DISTINCT unnest(filters || $1::text[])
            )
            WHERE telegram_id = $2
        """, [tag], user_id)

# Удалить фильтр из массива
async def remove_filter(user_id: int, tag: str):
    pool = get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE users
            SET filters = ARRAY(
                SELECT unnest(filters) EXCEPT SELECT $1
            )
            WHERE telegram_id = $2
        """, tag, user_id)