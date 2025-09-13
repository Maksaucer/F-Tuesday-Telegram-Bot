#filters.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardMarkup, KeyboardButton
from database.filters import get_filters, add_filter, remove_filter

async def get_filters_inline_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    filters = await get_filters(chat_id)

    nsfw_status = "✅ ВКЛ" if "nsfw" in filters else "❌ ВЫКЛ"
    male_status = "✅ ВКЛ" if "male/male" in filters else "❌ ВЫКЛ"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"🚫 NSFW: {nsfw_status}", callback_data="toggle_nsfw"),
                InlineKeyboardButton(text=f"🚫 Male/Male: {male_status}", callback_data="toggle_male"),
            ]
        ]
    )
    return keyboard

async def get_filters_menu(chat_id: int) -> ReplyKeyboardMarkup:
    filters = await get_filters(chat_id)

    nsfw_status = "🟢" if "nsfw" in filters else "🚫"
    gay_status = "🟢" if "male/male" in filters else "🚫"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"{nsfw_status} NSFW")],
            [KeyboardButton(text=f"{gay_status} GAY")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите фильтр"
    )

async def toggle_filter(chat_id: int, tag: str, message: Message):
    filters = await get_filters(chat_id)

    if tag in filters:
        await remove_filter(chat_id, tag)
        status = "🚫"
    else:
        await add_filter(chat_id, tag)
        status = "🟢"

    updated_menu = await get_filters_menu(chat_id)
    await message.answer(f"Фильтр `{tag}` теперь: *{status}*", parse_mode="Markdown", reply_markup=updated_menu)