#services/images.py

import logging
from config import E621_USERNAME, E621_API_KEY, USER_AGENT
from parsers.e621 import fetch_posts, fetch_random_post
from database.users import get_username, load_users
from database.filters import get_filters
from services.filters import is_post_allowed, get_rating_label
from aiogram import Bot

FURRY_TUESDAY_CAPTION = "😈 Добро пожаловать на фурри вторник! 😈\n"  # temporary


async def send_media(bot: Bot, user_id: int, file_url: str, file_ext: str, caption: str):
    try:
        if file_ext.lower() in ["jpg", "jpeg", "png"]:
            await bot.send_photo(user_id, file_url, caption=caption)
        elif file_ext.lower() == "gif":
            await bot.send_animation(user_id, file_url, caption=caption)
        elif file_ext.lower() == "webm":
            await bot.send_video(user_id, file_url, caption=caption)
        else:
            logging.warning(f"⚠️ Неподдерживаемый тип файла: {file_ext}")
            await bot.send_message(user_id, f"⚠️ Тип файла {file_ext} не поддерживается Telegram.")
    except Exception as e:
        logging.error(f"❌ Ошибка при отправке файла ({file_ext}): {e}")
        await bot.send_message(user_id, "❌ Произошла ошибка при отправке медиафайла.")


async def send_random_image(bot: Bot, user_id: int):
    filters = await get_filters(user_id)
    username = await get_username(user_id)

    for attempt in range(10):
        post = await fetch_random_post(E621_USERNAME, E621_API_KEY, USER_AGENT)
        if not post:
            break

        if not is_post_allowed(post, filters):
            logging.info(f"⛔ Пост {post['id']} содержит запрещённые теги для пользователя {user_id} - @{username}, пропущен.")
            continue

        file_url = post["file"]["url"]
        file_ext = post["file"]["ext"]
        post_url = f"https://e621.net/posts/{post['id']}"
        rating = get_rating_label(post.get("rating", ""))

        caption = f"{rating}\n{post_url}"

        await send_media(bot, user_id, file_url, file_ext, caption)
        logging.info(f"✅ Отправлен пост {post['id']} пользователю {user_id} - @{username} (рейтинг: {rating})")
        return

    await bot.send_message(user_id, "😞 Не удалось найти подходящую случайную картинку по вашим фильтрам.")


async def send_image(bot: Bot, user_id: int, period: str = "week", caption: str = ""):
    filters = await get_filters(user_id)
    username = await get_username(user_id)

    posts = await fetch_posts(E621_USERNAME, E621_API_KEY, USER_AGENT, period=period, limit=100 if caption == FURRY_TUESDAY_CAPTION else 50)

    if not posts:
        await bot.send_message(user_id, "😞 Не удалось найти подходящие картинки по вашим фильтрам.")
        return

    for idx, post in enumerate(posts, start=1):
        if not is_post_allowed(post, filters):
            logging.info(f"⛔ Пост {post['id']} содержит запрещённые теги для пользователя {user_id} - @{username}, пропущен. #post[{idx}]")
            continue

        file_url = post["file"]["url"]
        file_ext = post["file"]["ext"]
        post_url = f"https://e621.net/posts/{post['id']}"
        rating = get_rating_label(post.get("rating", ""))

        full_caption = caption + f"{rating}\n{post_url}"

        await send_media(bot, user_id, file_url, file_ext, full_caption)
        logging.info(f"✅ Отправлен пост {post['id']} пользователю {user_id} - @{username} (рейтинг: {rating})")
        return

    if caption == FURRY_TUESDAY_CAPTION:
        await bot.send_message(user_id, "😞 Фурри вторник отменён — у вас слишком строгие фильтры или запрещён NSFW.")
    else:
        await bot.send_message(user_id, "😞 Не удалось найти подходящую картинку по вашим фильтрам.")


async def send_image_toeveryone(bot: Bot, period: str = "week"):
    users = await load_users()
    for user_id in users:
        try:
            await send_image(bot, user_id, period=period, caption=FURRY_TUESDAY_CAPTION)
        except Exception as e:
            logging.warning(f"❌ Не удалось отправить сообщение пользователю {user_id}: {e}")