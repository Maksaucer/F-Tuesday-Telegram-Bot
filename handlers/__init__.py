#handlers/__init__.py

from aiogram import Router
from .start import router as start_router
from .buttons import router as buttons_router
from .callbacks import router as callbacks_router

router = Router()
router.include_router(start_router)
router.include_router(buttons_router)
router.include_router(callbacks_router)
