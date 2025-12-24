from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.repo import Repos


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: Message, data: dict) -> bool:
        repos: Repos = data.get("repos")
        if not repos:
            return False
        return await repos.user.is_exist(message.from_user.id)


class NotRegisteredFilter(BaseFilter):
    async def __call__(self, message: Message, data: dict) -> bool:
        repos: Repos = data.get("repos")
        if not repos:
            return False
        return not await repos.user.is_exist(message.from_user.id)