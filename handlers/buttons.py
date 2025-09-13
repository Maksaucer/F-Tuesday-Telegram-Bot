#handlers/buttons.py

import time
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from keyboards import main_menu, get_image_menu, period_menu
from services.images import send_random_image, send_image
from services.filters import get_filters_inline_keyboard
from database.users import add_user, get_username, unsubscribe_user

router = Router()

# Храним время последнего запроса для каждого пользователя
user_cooldowns = {}

# время кулдауна в секундах (например, 10 секунд)
COOLDOWN_SECONDS = 1

@router.message()
async def handle_buttons(message: Message):
    user_id = message.chat.id
    username = await get_username(user_id)
    await add_user(user_id, username)
    text = message.text
    bot = message.bot

    match text:
        case "🔞 Получить картинку":
            await message.answer("Выберите тип картинки:", reply_markup=get_image_menu)

        case "🎲 Случайная картинка":
            now = time.time()
            last_used = user_cooldowns.get(user_id, 0)
            if now - last_used < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - (now - last_used))
                await message.answer(f"⏳ Подожди {remaining+1} сек перед следующей случайной картинкой!")
                return
            user_cooldowns[user_id] = now
            await send_random_image(bot, user_id)

        case "🕰 Лучшая за период":
            await message.answer("Выберите период:", reply_markup=period_menu)
        case "🥉 За день":
            await send_image(bot, user_id, period="day")
        case "🥈 За неделю":
            await send_image(bot, user_id, period="week")
        case "🥇 За месяц":
            await send_image(bot, user_id, period="month")
        case "⚙️ Фильтры":
            keyboard = await get_filters_inline_keyboard(user_id)
            await message.answer("Настройка фильтров:", reply_markup=keyboard)
        case "❌ Отписаться":
            await unsubscribe_user(user_id)
            await message.answer("Вы отписались от рассылки 📴", reply_markup=ReplyKeyboardRemove())
        case "🔙 Назад":
            await message.answer("Главное меню:", reply_markup=main_menu)
        case _:
            await message.answer("Я не понимаю эту команду. Используй кнопки, балбес >:T")