from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import main_menu
from database.users import add_user, get_username
import logging

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.chat.id
    username = message.from_user.username
    logging.info(f"▶️ /start от пользователя {user_id}")
    await add_user(user_id, username)
    await message.answer(
        "Привет! Я бот, который отправляет картинки с e621. Выбери действие:",
        reply_markup=main_menu
    )
