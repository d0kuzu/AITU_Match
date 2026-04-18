from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from database.repo import Repos

class BanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        repos: Repos = data.get("repos")
        if not repos:
            return await handler(event, data)

        if await repos.ban.is_banned(user.id):
            if isinstance(event, Message):
                await event.answer("Вы заблокированы в системе.")
            return

        return await handler(event, data)
