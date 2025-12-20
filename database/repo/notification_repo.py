import logging

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.notification import Notification
from database.repo.repo import Repo


class NotificationRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create_notification(self, action_id: int):
        try:
            async with self.session.begin():
                stmt = Notification(
                    action_id=action_id,
                )

                await self.session.merge(stmt)
        except Exception as e:
            logging.error(f"notification_repo.create_notification {action_id}: {e}")
            return None
