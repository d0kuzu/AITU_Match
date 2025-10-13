from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import database.repo as repo
from database.repo.repo import Repo
from database.session import get_db


class RepoMiddleware(BaseMiddleware):
    def __init__(self, user_repo: Repo):
        self.user_repo = user_repo

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

            data["user_repo"] = self.user_repo

            return await handler(event, data)
