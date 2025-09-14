#parsers/e621.py

import random
import logging
from aiohttp import ClientSession, BasicAuth
from config import PROXY_URL

try:
    # Для SOCKS5-прокси (если не установлен пакет — используем HTTP(S) вариант)
    from aiohttp_socks import ProxyConnector # type: ignore
except Exception:
    ProxyConnector = None # noqa: N816

def _make_session(proxy_url: str | None) -> ClientSession:
    timeout = ClientTimeout(total=15)
    if proxy_url:
        if proxy_url.startswith(("socks5://", "socks4://")):
            if not ProxyConnector:
                raise RuntimeError("Для SOCKS-прокси установи пакет: pip install aiohttp-socks")
            connector = ProxyConnector.from_url(proxy_url) # remote DNS по умолчанию
            return ClientSession(connector=connector, timeout=timeout)
            # Для HTTP/HTTPS-прокси — создаём обычную сессию, а прокси передаём в запрос
        return ClientSession(timeout=timeout)
    return ClientSession(timeout=timeout)

def _req_proxy_kwargs(proxy_url: str | None) -> dict:
# Для HTTP/HTTPS прокси передаём proxy=... на уровне запроса
    if proxy_url and not proxy_url.startswith(("socks5://", "socks4://")):
        return {"proxy": proxy_url}
    return {}

async def fetch_posts(username: str, api_key: str, user_agent: str, period: str = "day", limit: int = 10, proxy_url: str | None = None):
    proxy_url = proxy_url or (PROXY_URL or None)
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'limit': limit,
        'tags': f"order:score date:{period}"
    }

    async with _make_session(proxy_url) as session:
        try:
            async with session.get(
                url,
                headers=headers,
                params=params,
                auth=BasicAuth(username, api_key),
                **_req_proxy_kwargs(proxy_url),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    posts = data.get("posts") or []
                    return posts
                text = await resp.text()
                logging.error("e621 error %s: %s", resp.status, text[:300])
                return []
        except Exception as e:
            logging.error("Request to e621 failed: %s", e)
            return []

async def fetch_random_post(username: str, api_key: str, user_agent: str, proxy_url: str | None = None):
    proxy_url = proxy_url or (PROXY_URL or None)
    url = 'https://e621.net/posts.json'
    headers = {
        'User-Agent': user_agent
    }
    params = {
        'limit': 10,
        'tags': 'order:random'
    }

    async with _make_session(proxy_url) as session:
        try:
            async with session.get(
                url,
                headers=headers,
                params=params,
                auth=BasicAuth(username, api_key),
                **_req_proxy_kwargs(proxy_url),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    posts = data.get("posts") or []
                    return random.choice(posts) if posts else None
                text = await resp.text()
                logging.error("e621 error %s: %s", resp.status, text[:300])
                return None
        except Exception as e:
            logging.error("Random request to e621 failed: %s", e)
            return None