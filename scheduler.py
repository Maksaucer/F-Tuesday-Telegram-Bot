#scheduler.py

import datetime
import asyncio
from services.images import send_image_toeveryone

async def scheduler(bot):
    while True:
        now = datetime.datetime.now()
        if now.weekday() == 1:
            await send_image_toeveryone(bot, period="week")
            await asyncio.sleep(24 * 3600)
        else:
            await asyncio.sleep(24 * 3600)