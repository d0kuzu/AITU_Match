from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import database.repo as repo
from database.repo.repo import Repo
from database.session import get_db


class RepoMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with get_db() as session:
            user_repo = repo.UserRepo(session)
        data["user_repo"] = user_repo

        return await handler(event, data)
