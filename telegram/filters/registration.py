from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.repo import UserRepo
from database.session import get_db


class RegisteredFilter(BaseFilter):
    async def __call__(self, message: Message, user_repo: UserRepo) -> bool:
        is_exist = await user_repo.is_exist(message.from_user.id)
        return is_exist
