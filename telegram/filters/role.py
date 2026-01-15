from aiogram.filters import BaseFilter
from aiogram.types import Message

from config.config import env, Environ


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in Environ().bot.admin_ids
