# web_service.py
# Нежеланный ребенок этого кода. Нужен только, чтобы хостинг не ругался на порт
import os
import asyncio  
import logging
import contextlib
from aiohttp import web

# твой бот и корутина запуска
from bot import main as run_bot, bot as tg_bot
from services.images import send_image_toeveryone

CRON_SECRET = os.getenv("CRON_SECRET", "")  # опциональный секрет для /broadcast

async def health(_request: web.Request) -> web.Response:
    return web.Response(text="OK")

async def broadcast(request: web.Request) -> web.Response:
    # Простой «крон-эндпоинт» для триггера рассылки: /broadcast?period=week&key=SECRET
    if CRON_SECRET:
        if request.query.get("key") != CRON_SECRET:
            return web.json_response({"ok": False, "error": "forbidden"}, status=403)

    period = request.query.get("period", "week")
    await send_image_toeveryone(tg_bot, period=period)
    return web.json_response({"ok": True, "period": period})

async def on_startup(app: web.Application) -> None:
    # Запускаем бота (polling) в бэкграунде
    app["bot_task"] = asyncio.create_task(run_bot())
    logging.info("Bot task started.")

async def on_cleanup(app: web.Application) -> None:
    task: asyncio.Task | None = app.get("bot_task")
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

def create_app() -> web.Application:
    app = web.Application()
    app.add_routes([
        web.get("/", health),
        web.get("/health", health),
        web.get("/ping", health),
        web.get("/broadcast", broadcast),   # GET для простых пингов
        web.post("/broadcast", broadcast),  # POST если захочешь вызывать кроном
    ])
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = int(os.getenv("PORT", "8000"))
    web.run_app(create_app(), host="0.0.0.0", port=port)