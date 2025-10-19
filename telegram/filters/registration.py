from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.repo import UserRepo, Repos
from database.session import get_db


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: Message, repos: Repos) -> bool:
        is_exist = await repos.user.is_exist(message.from_user.id)
        return is_exist
