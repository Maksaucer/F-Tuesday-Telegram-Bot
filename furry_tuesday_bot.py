import logging
import os
import asyncio
from user_storage import *
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiohttp import ClientSession, BasicAuth

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

# Логирование
logging.basicConfig(level=logging.INFO)

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔞 Получить картинку")],
        [KeyboardButton(text="❌ Отписаться")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

# Меню выбора периода картинки 
period_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🥉 За день")],
        [KeyboardButton(text="🥈 За неделю")],
        [KeyboardButton(text="🥇 За месяц")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите период"
)


# === ASYNC ФУНКЦИИ === 


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

# Функция отправки картинки
async def send_image(chat_id: int, period: str = "day"):
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': USER_AGENT
    }
    params = {
        'limit': 1,
        'tags': f"order:score date:{period}"
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
                    if data and data.get("posts"):
                        post = data["posts"][0]
                        image_url = post["sample"]["url"]
                        post_url = f"https://e621.net/posts/{post['id']}"

                        await bot.send_photo(chat_id, image_url, caption=post_url)
                        logging.info(f"✅ Sent image to {chat_id}")
                    else:
                        await bot.send_message(chat_id, "😞 Картинки не найдены.")
                else:
                    logging.error(f"❌ Error fetching data: {resp.status}")
        except Exception as e:
            logging.error(f"❌ Failed to send image to {chat_id}: {e}")



async def send_image_toeveryone(period="day"):
    users = load_users()

    for user_id in users:
        try:
            await send_image(user_id, period=period)
        except Exception as e:
            logging.warning(f"❌ Не удалось отправить сообщение {user_id}: {e}")


# Автоматическая отправка по расписанию 
async def scheduler():
    while True:
        await asyncio.sleep(3600)  # каждый час
        await send_image_toeveryone(period="day")

# Запуск бота
async def main():
    dp.include_router(router)
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)


# === КОМАНДЫ ===


# Команда /start
@router.message(Command("start"))
async def start_handler(message: Message):
    chat_id = message.chat.id
    print(f"▶️ /start от пользователя {chat_id}")
    add_user(chat_id)
    await message.answer(
        "Привет! Я бот, который отправляет самую популярную картинку с e621. Выбери действие:",
        reply_markup=main_menu
    )

# Кнопка "Получить картинку"
@router.message()
async def handle_buttons(message: Message):
    chat_id = message.chat.id
    text = message.text

    text = message.text

    match text:
        case "🔞 Получить картинку":
            await message.answer("Выбери период:", reply_markup=period_menu)

        case "🥉 За день":
            await send_image(chat_id, period="day")

        case "🥈 За неделю":
            await send_image(chat_id, period="week")

        case "🥇 За месяц":
            await send_image(chat_id, period="month")

        case "🔙 Назад":
            await message.answer("Вы вернулись в главное меню:", reply_markup=main_menu)

        case "❌ Отписаться":
            from user_storage import remove_user
            remove_user(chat_id)
            await message.answer("Вы отписались от рассылки 📴", reply_markup=ReplyKeyboardRemove())

        case _:
            await message.answer("Я не понимаю эту команду. Используй КНОПКИ, дурень >:T")


# === ЗАПУСК ===


if __name__ == "__main__":
    asyncio.run(main())