from datetime import time, datetime
from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import database.repo as repo
from config.config import Environ
from database.repo.repo import Repo
from database.session import get_db


class LastActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        data["last_activity"] = datetime.now()
        return await handler(event, data)
