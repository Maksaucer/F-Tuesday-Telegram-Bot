import logging
import os
import datetime
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Дополнительно
from user_storage import *

# Импортируем функцию из e621_parser.py
from E621_parser import *

# Загружаем переменные окружения из .env
load_dotenv()

# Ключи
TOKEN = os.getenv("TOKEN")
E621_USERNAME = os.getenv("E621_USERNAME")
E621_API_KEY = os.getenv("E621_API_KEY")
USER_AGENT = 'FurryTuesdayBot/1.0 (by @maksaucer)'

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


# === ФУНКЦИИ ===

async def send_image(chat_id: int, period: str = "week"):
    post = await fetch_post(E621_USERNAME, E621_API_KEY, USER_AGENT, period=period)
    if not post:
        await bot.send_message(chat_id, "😞 Картинки не найдены.")
        return  

    # Извлекаем данные из поста
    image_url = post["sample"]["url"]   
    post_url = f"https://e621.net/posts/{post['id']}"

    try:
        await bot.send_photo(chat_id, image_url, caption=post_url)
        logging.info(f"✅ Отправлена картинка пользователю {chat_id}")
    except Exception as e:
        logging.error(f"❌ Не удалось отправить картинку пользователю {chat_id}: {e}")


async def send_image_toeveryone(period="week"):
    users = load_users()
    for user_id in users:
        try:
            await send_image(user_id, period=period)
        except Exception as e:
            logging.warning(f"❌ Не удалось отправить сообщение {user_id}: {e}")

# Автоматическая отправка по расписанию (пример: раз в час)
async def scheduler():
    while True:
        now = datetime.datetime.now()
        if now.weekday() == 1: # Вторник=1, 
            await send_image_toeveryone(period="day")
            await asyncio.sleep(24 * 3600)
        else:
            # Повторная проверка через 24 часа
            await asyncio.sleep(24 * 3600)


# Запуск бота
async def main():
    dp.include_router(router)
    # Запускаем шедулер в фоне
    asyncio.create_task(scheduler())
    # Стартуем лонг-поллинг
    await dp.start_polling(bot)


# === Хэндлеры ===

@router.message(Command("start"))
async def start_handler(message: Message):
    chat_id = message.chat.id
    print(f"▶️ /start от пользователя {chat_id}")
    add_user(chat_id)
    await message.answer(
        "Привет! Я бот, который отправляет самую популярную картинку с e621. Выбери действие:",
        reply_markup=main_menu
    )

@router.message()
async def handle_buttons(message: Message):
    chat_id = message.chat.id
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
            remove_user(chat_id)
            await message.answer("Вы отписались от рассылки 📴", reply_markup=ReplyKeyboardRemove())

        case _:
            await message.answer("Я не понимаю эту команду. Используй КНОПКИ, дурень >:T")


if __name__ == "__main__":
    asyncio.run(main())