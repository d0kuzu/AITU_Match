from aiogram import Bot

from database.repo import Repos
from database.session import get_db


async def noification_sender(bot: Bot):
    async with get_db() as session:
        repos = Repos(session)

        notifications = await repos.notification.get_available()

        for notification in notifications:
