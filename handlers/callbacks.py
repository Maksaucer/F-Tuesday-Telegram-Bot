#handlers/callbacks.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from services.filters import get_filters_inline_keyboard
from database.filters import get_filters, add_filter, remove_filter

router = Router()

@router.callback_query(F.data.startswith("toggle_"))
async def handle_filter_toggle(callback: CallbackQuery):
    tag_map = {
        "toggle_nsfw": "nsfw",
        "toggle_gay": "gay"
    }

    tag = tag_map.get(callback.data)
    chat_id = callback.from_user.id

    if not tag:
        await callback.answer("Неизвестный фильтр.", show_alert=True)
        return

    filters = await get_filters(chat_id)

    if tag in filters:
        await remove_filter(chat_id, tag)
        status = "❌ ВЫКЛ"
    else:
        await add_filter(chat_id, tag)
        status = "✅ ВКЛ"

    new_keyboard = await get_filters_inline_keyboard(chat_id)
    await callback.message.edit_reply_markup(reply_markup=new_keyboard)
    await callback.answer(f"Фильтр {tag} теперь {status}")