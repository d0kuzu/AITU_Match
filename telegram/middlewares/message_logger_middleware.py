from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject
from typing import Callable, Dict, Any
from datetime import datetime

from database.repo import UserRepo


class MessageLoggerMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Any],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_repo = data["user_repo"]
            await self.save_message(user_repo, event)

        return await handler(event, data)

    async def save_message(self, user_repo: UserRepo, message: Message) -> None:
        await user_repo.add_message(message.from_user.id, message.message_id)
