#bot.py

import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN
from database import init_db, get_db_pool
from handlers import router
from scheduler import scheduler

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Создание экземпляров бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    # Инициализация пула соединений с БД
    await init_db()

    # Проверка, что пул успешно создан
    if get_db_pool() is None:
        logging.error("❌ Database pool is still None after initialization.")
        return

    logging.info("✅ Database pool initialized and ready to use.")

    # Подключаем роутеры
    dp.include_router(router)

    # Запуск планировщика задач
    asyncio.create_task(scheduler(bot))

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())