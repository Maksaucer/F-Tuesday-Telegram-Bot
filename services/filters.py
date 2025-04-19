from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database.filters import get_filters, add_filter, remove_filter

async def get_filters_inline_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    filters = await get_filters(chat_id)
    nsfw_status = "✅ ВКЛ" if "nsfw" in filters else "❌ ВЫКЛ"
    male_status = "✅ ВКЛ" if "male/male" in filters else "❌ ВЫКЛ"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"🚫 NSFW: {nsfw_status}", callback_data="toggle_nsfw"),
                InlineKeyboardButton(text=f"🚫 Male/Male: {male_status}", callback_data="toggle_male"),
            ]
        ]
    )

def get_rating_label(rating: str) -> str:
    rating = rating.lower()
    match rating:
        case "s":
            return "✅ Safe"
        case "q":
            return "⚠️ Questionable"
        case "e":
            return "🔞 Explicit"
        case _:
            return "❔ Unknown"

def is_post_allowed(post: dict, filters: list[str]) -> bool:
    if not filters:
        return True  # Нет фильтров — всё позволено

    # Приведение к нижнему регистру
    filters = set(tag.lower() for tag in filters)

    # --- 1. Проверка NSFW по рейтингу ---
    rating = post.get("rating", "").lower()  # может быть "e", "q", "s"
    if "nsfw" in filters and rating in ("e", "q"):
        return False


    # --- 2. Проверка обычных тегов ---
    tags = []
    for tag_list in post.get("tags", {}).values():
        tags.extend(tag_list)

    tags = set(tag.lower() for tag in tags)

    return not filters.intersection(tags)