from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from database.filters import get_filters, add_filter, remove_filter

async def get_filters_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    filters = await get_filters(user_id)
    nsfw_status = "✅ ВКЛ" if "nsfw" in filters else "❌ ВЫКЛ"
    male_status = "✅ ВКЛ" if "gay" in filters else "❌ ВЫКЛ"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"🚫 NSFW: {nsfw_status}", callback_data="toggle_nsfw"),
                InlineKeyboardButton(text=f"🚫 GAY: {male_status}", callback_data="toggle_gay"),
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
    # Приведение фильтров к нижнему регистру
    filters = set(tag.lower() for tag in filters)
    # Форматы изображений
    IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

    # --- 0. Проверка по расширению файла
    file_ext = post.get("file", {}).get("ext", "").lower()
    print(file_ext)
    if file_ext not in IMAGE_EXTENSIONS:
        return False

    # --- 1. Сбор всех тегов из поста ---
    tags = []
    for tag_list in post.get("tags", {}).values():
        tags.extend(tag_list)
    tags = set(tag.lower() for tag in tags)

    # --- 2. Жесткий фильтр по ужасным тегам ---
    if {"gore", "feces", "urine", "diaper", "young", "loli", "shota", "pregnant"}.intersection(tags):
        return False

    # --- 3. Проверка на фильтры пользователя
    if not filters:
        return True  # Нет фильтров — В С Е

    # --- 4. Проверка NSFW по рейтингу ---
    rating = post.get("rating", "").lower()
    if "nsfw" in filters and rating in ("e", "q"):
        return False

    # --- ВРЕМЕННАЯ логика для исключений---
    if "gay" in filters and "male" in tags and "female" not in tags:
        return False

    # --- 5. Обычная фильтрация по тегам ---
    if filters.intersection(tags):
        return False

    return True  # Всё прошло — пост разрешён
