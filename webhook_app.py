# webhook_app.py
"""
Запуск бота в режиме webhook для Render Web Service.

Пути:
- GET /health      -> health-check
- GET/POST /broadcast?period=week&key=... -> ручной триггер рассылки
- POST /tg/webhook -> входящие апдейты Telegram (вебхук)

Start command на Render:  python webhook_app.py
"""

import os
import asyncio
import logging
import contextlib
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers import router as handlers_router
from database import init_db
from services.images import send_image_toeveryone
from bot import bot as tg_bot, dp as tg_dp  # объекты Bot и Dispatcher из твоего bot.py

# -------- Конфигурация из окружения --------
WEBHOOK_BASE = (os.getenv("WEBHOOK_BASE") or os.getenv("RENDER_EXTERNAL_URL") or "").rstrip("/")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/tg/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # опционально: для заголовка X-Telegram-Bot-Api-Secret-Token
CRON_SECRET = os.getenv("CRON_SECRET", "")        # опционально: защита эндпоинта /broadcast
PORT = int(os.getenv("PORT", "8000"))

if not WEBHOOK_BASE:
    raise RuntimeError(
        "WEBHOOK_BASE не задан. В Render → Environment добавь переменную WEBHOOK_BASE "
        "со значением вроде https://<service-name>.onrender.com"
    )

WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"

# -------- HTTP handlers --------
async def health(_request: web.Request) -> web.Response:
    return web.Response(text="OK")

async def broadcast(request: web.Request) -> web.Response:
    if CRON_SECRET and request.query.get("key") != CRON_SECRET:
        return web.json_response({"ok": False, "error": "forbidden"}, status=403)
    period = request.query.get("period", "week")
    await send_image_toeveryone(tg_bot, period=period)
    return web.json_response({"ok": True, "period": period})

# -------- aiogram lifecycle --------
async def set_webhook(bot: Bot):
    # Сбрасываем старые апдейты и ставим вебхук
    await bot.set_webhook(
        url=WEBHOOK_URL,
        secret_token=WEBHOOK_SECRET or None,
        drop_pending_updates=True,
        allowed_updates=tg_dp.resolve_used_update_types(),
    )
    logging.info("Webhook set to %s", WEBHOOK_URL)

async def delete_webhook(bot: Bot):
    with contextlib.suppress(Exception):
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Webhook deleted")

async def on_startup(app: web.Application):
    # Роутеры
    tg_dp.include_router(handlers_router)
    # Инициализация БД
    await init_db()
    # Вебхук
    await set_webhook(tg_bot)

    # (опционально) запустить твой планировщик в фоне.
    # Помни: на бесплатном Render сервис может «уснуть», и тогда цикл не сработает.
    from scheduler import scheduler
    app["scheduler_task"] = asyncio.create_task(scheduler(tg_bot))
    logging.info("Scheduler task started")

async def on_cleanup(app: web.Application):
    task: asyncio.Task | None = app.get("scheduler_task")
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    await delete_webhook(tg_bot)

# -------- сборка и запуск aiohttp-приложения --------
def create_app() -> web.Application:
    logging.basicConfig(level=logging.INFO)
    app = web.Application()

    # Служебные роуты
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    app.router.add_get("/ping", health)
    app.router.add_get("/broadcast", broadcast)
    app.router.add_post("/broadcast", broadcast)

    # Роут для Telegram-апдейтов
    req_handler = SimpleRequestHandler(dispatcher=tg_dp, bot=tg_bot, secret_token=WEBHOOK_SECRET or None)
    req_handler.register(app, path=WEBHOOK_PATH)

    # Подцепляем хуки старта/остановки aiogram
    setup_application(app, dispatcher=tg_dp, bot=tg_bot)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=PORT)