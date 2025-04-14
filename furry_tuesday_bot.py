import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiohttp import ClientSession, BasicAuth
from aiogram import Router

# Загружаем переменные окружения из .env
load_dotenv()

# Ключи
TOKEN = os.getenv("TOKEN")
E621_USERNAME = os.getenv("E621_USERNAME")
E621_API_KEY = os.getenv("E621_API_KEY")
USER_AGENT = 'FurryTuesdayBot/1.0 (by @me)'

# Иниициалищация
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
chat_id = None

# Логирование
logging.basicConfig(level=logging.INFO)

# Получить картинку с e621
async def get_most_image_data():
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': USER_AGENT
    }
    params = {
        'limit': 1,
        'tags': 'order:score date:day'
    }

    async with ClientSession() as session:
        try:
            async with session.get(
                url,
                headers=headers,
                params=params,
                auth=BasicAuth(E621_USERNAME, E621_API_KEY)) as resp:
                
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    logging.error(f"Error fetching data: {resp.status}")
        except Exception as e:
            logging.error(f"Request failed: {e}")
    return None

# Команда /start
@router.message(Command("start"))
async def start_handler(message: Message):
    global chat_id
    chat_id = message.chat.id
    await message.answer("Привет! Я бот, который отправляет самую популярную картинку с e621. Напиши /porn!")

# Команда /porn
@router.message(Command("porn"))
async def porn_handler(message: Message):
    await send_image()

# Функция отправки картинки
async def send_image():
    global chat_id
    if chat_id is not None:
        data = await get_most_image_data()
        if data and data.get("posts"):
            post = data["posts"][0]
            image_url = post["sample"]["url"]
            post_url = f"https://e621.net/posts/{post['id']}"
            try:
                await bot.send_photo(chat_id, image_url, caption=post_url)
                logging.info(f"Sent image to {chat_id}")
            except Exception as e:
                logging.error(f"Failed to send image: {e}")
        else:
            logging.warning("No image data received.")

# Автоматическая отправка по расписанию 
async def scheduler():
    while True:
        await send_image()
        await asyncio.sleep(600)  # каждые 10 минут

# Запуск бота
async def main():
    dp.include_router(router)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())