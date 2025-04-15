import logging
import os
import datetime
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Импортируем ВСЕ функции из user_storage.py
from user_storage import *

    # Импортируем ВСЕ функции из e621_parser.py
from E621_parser import *

# Загружаем переменные окружения из .env
load_dotenv()

# Ключи
TOKEN = os.getenv("TOKEN")
E621_USERNAME = os.getenv("E621_USERNAME")
E621_API_KEY = os.getenv("E621_API_KEY")
USER_AGENT = 'FurryTuesdayBot/1.0 (by @maksaucer)'

# Инициализация
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

# Меню «Получить картинку»
# 1) Случайная
# 2) Лучшая за период (ведёт к period_menu)
get_image_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎲 Случайная картинка")],
        [KeyboardButton(text="🕰 Лучшая за период")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

# Меню выбора периода картинки (подменю «Лучшая за период»)
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

async def send_random_image(chat_id: int):
    """
    Отправить случайную картинку пользователю chat_id
    """
    post = await fetch_random_post(E621_USERNAME, E621_API_KEY, USER_AGENT)
    if not post:
        await bot.send_message(chat_id, "😞 Случайных картинок не найдено.")
        return

    image_url = post["sample"]["url"]
    post_url = f"https://e621.net/posts/{post['id']}"

    try:
        await bot.send_photo(chat_id, image_url, caption=post_url)
        logging.info(f"✅ Отправлена случайная картинка пользователю {chat_id}")
    except Exception as e:
        logging.error(f"❌ Не удалось отправить случайную картинку пользователю {chat_id}: {e}")


async def send_image(chat_id: int, period: str = "week"):
    """
    Отправить самую популярную картинку за period (по умолчанию за неделю).
    """
    post = await fetch_post(E621_USERNAME, E621_API_KEY, USER_AGENT, period=period)
    if not post:
        await bot.send_message(chat_id, "😞 Картинки не найдены.")
        return

    image_url = post["sample"]["url"]
    post_url = f"https://e621.net/posts/{post['id']}"

    try:
        await bot.send_photo(chat_id, image_url, caption=post_url)
        logging.info(f"✅ Отправлена картинка пользователю {chat_id}")
    except Exception as e:
        logging.error(f"❌ Не удалось отправить картинку пользователю {chat_id}: {e}")


async def send_image_toeveryone(period="week"):
    """
    Рассылка самой популярной картинки за выбранный period всем пользователям
    """
    users = load_users()
    for user_id in users:
        try:
            await send_image(user_id, period=period)
        except Exception as e:
            logging.warning(f"❌ Не удалось отправить сообщение {user_id}: {e}")


# Автоматическая отправка раз в сутки, по вторникам
async def scheduler():
    while True:
        now = datetime.datetime.now()
        if now.weekday() == 1:  # Понедельник=0, Вторник=1
            await send_image_toeveryone(period="day")
            # Засыпаем на 24 часа, чтобы не отправлять повторно в тот же вторник
            await asyncio.sleep(24 * 3600)
        else:
            # Проверяем снова через 24 часа
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
        "Привет! Я бот, который отправляет картинки с e621. Выбери действие:",
        reply_markup=main_menu
    )


@router.message()
async def handle_buttons(message: Message):
    chat_id = message.chat.id
    text = message.text

    match text:
        # 1. Пользователь нажал «Получить картинку» в главном меню
        case "🔞 Получить картинку":
            await message.answer("Выберите тип картинки:", reply_markup=get_image_menu)

        # 2. Подменю «Получить картинку»
        case "🎲 Случайная картинка":
            await send_random_image(chat_id)

        case "🕰 Лучшая за период":
            await message.answer("Выберите период:", reply_markup=period_menu)

        # 3. Подменю «Лучшая за период»
        case "🥉 За день":
            await send_image(chat_id, period="day")

        case "🥈 За неделю":
            await send_image(chat_id, period="week")

        case "🥇 За месяц":
            await send_image(chat_id, period="month")

        # Возврат в меню
        case "🔙 Назад":
            # При нажатии «Назад» — возвращаемся в главное меню
            await message.answer("Главное меню:", reply_markup=main_menu)

        # Кнопка «Отписаться»
        case "❌ Отписаться":
            remove_user(chat_id)
            await message.answer("Вы отписались от рассылки 📴", reply_markup=ReplyKeyboardRemove())

        # Что-то непонятное
        case _:
            await message.answer("Я не понимаю эту команду. Пожалуйста, воспользуйтесь кнопками.")


if __name__ == "__main__":
    asyncio.run(main())