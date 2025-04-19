import logging
from config import E621_USERNAME, E621_API_KEY, USER_AGENT
from parsers.e621 import fetch_post, fetch_random_post
from database.users import get_username, load_users
from database.filters import get_filters
from services.filters import is_post_allowed, get_rating_label
from aiogram import Bot

async def send_random_image(bot: Bot, user_id: int):
    filters = await get_filters(user_id)
    username = await get_username(user_id)

    for attempt in range(10):
        post = await fetch_random_post(E621_USERNAME, E621_API_KEY, USER_AGENT)
        if not post:
            break

        if not is_post_allowed(post, filters):
            logging.info(f"⛔ Случайный пост {post['id']} содержит запрещённые теги для пользователя {user_id} - @{username}, пропущен.")
            continue

        image_url = post["sample"]["url"]
        post_url = f"https://e621.net/posts/{post['id']}"
        rating = get_rating_label(post.get("rating", ""))

        caption = f"{rating}\n{post_url}"
        try:
            await bot.send_photo(user_id, image_url, caption=caption)
            logging.info(f"✅ Отправлена случайная картинка пользователю {user_id} - @{username} (рейтинг: {rating})")
        except Exception as e:
            logging.error(f"❌ Не удалось отправить случайную картинку пользователю {user_id} - @{username}: {e}")
        return

    await bot.send_message(user_id, "😞 Не удалось найти подходящую случайную картинку по вашим фильтрам.")

async def send_image(bot: Bot, user_id: int, period: str = "week"):
    filters = await get_filters(user_id)
    username = await get_username(user_id)

    for attempt in range(10):
        post = await fetch_post(E621_USERNAME, E621_API_KEY, USER_AGENT, period=period)
        if not post:
            break

        if not is_post_allowed(post, filters):
            logging.info(f"⛔ Пост {post['id']} содержит запрещённые теги для пользователя {user_id} - @{username}, пропущен.")
            continue

        image_url = post["sample"]["url"]
        post_url = f"https://e621.net/posts/{post['id']}"
        rating = get_rating_label(post.get("rating", ""))

        caption = f"{rating}\n{post_url}"

        try:
            await bot.send_photo(user_id, image_url, caption=caption)
            logging.info(f"✅ Отправлена картинка пользователю {user_id} - @{username} (рейтинг: {rating})")
        except Exception as e:
            logging.error(f"❌ Не удалось отправить картинку пользователю {user_id} - @{username}: {e}")
        return

    await bot.send_message(user_id, "😞 Не удалось найти подходящую картинку по вашим фильтрам.")

async def send_image_toeveryone(bot: Bot, period="week"):
    users = await load_users()
    for user_id in users:
        try:
            await send_image(bot, user_id, period=period)
        except Exception as e:
            logging.warning(f"❌ Не удалось отправить сообщение {user_id}: {e}")
