import random
import logging
from aiohttp import ClientSession, BasicAuth

async def fetch_post(e621_username: str, e621_api_key: str, user_agent: str, period: str = "day"):
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'limit': 1,
        'tags': f"order:score date:{period}"
    }

    async with ClientSession() as session:  
        try:
            async with session.get(
                url,
                headers=headers,
                params=params,
                auth=BasicAuth(e621_username, e621_api_key)
            ) as resp:

                if resp.status == 200:
                    data = await resp.json()
                    if data and data.get("posts"):
                        return data["posts"][0]  # Возвращаем один первый пост
                    else:
                        logging.info("Посты не найдены")
                        return None
                else:
                    logging.error(f"Ошибка при получении данных: {resp.status}")
                    return None

        except Exception as e:
            logging.error(f"Не удалось выполнить запрос к e621: {e}")
            return None

async def fetch_random_post(e621_username: str, e621_api_key: str, user_agent: str):
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'limit': 10,            #
        'tags': 'order:random'  
    }

    async with ClientSession() as session:
        try:
            async with session.get(
                url,
                headers=headers,
                params=params,
                auth=BasicAuth(e621_username, e621_api_key)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    posts = data.get("posts", [])
                    if not posts:
                        logging.info("Случайные посты не найдены.")
                        return None
                    return random.choice(posts)  # Выбираем любой из полученных
                else:
                    logging.error(f"Ошибка при GET-запросе: {resp.status}")
                    return None
        except Exception as e:
            logging.error(f"Не удалось выполнить GET-запрос k e621: {e}")
            return None
    