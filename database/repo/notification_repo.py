import logging
from typing import Any, Coroutine, Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import NotificationStateEnum
from database.models.notification import Notification
from database.repo.repo import Repo


class NotificationRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def get_available(self) -> Sequence[Notification] | None:
        try:
            async with self.session.begin():
                stmt = (
                    select(Notification)
                    .options(selectinload(Notification.action))
                    .order_by(Notification.id.desc())
                ) # TODO: check user for is_active
                result = await self.session.execute(stmt)
                notifications = result.scalars().all()
            return notifications
        except Exception as e:
            logging.error(f"notification_repo.get_available error: {e}")
            return None


    async def create_notification(self, action_id: int):
        try:
            async with self.session.begin():
                stmt = Notification(
                    action_id=action_id,
                    state=NotificationStateEnum.WAITING,
                )

                await self.session.merge(stmt)
        except Exception as e:
            logging.error(f"notification_repo.create_notification error {action_id}: {e}")
            return None


    async def delete_notification(self, action_id: int):
        try:
            async with self.session.begin():
                stmt = (
                    delete(Notification)
                    .where(Notification.id == action_id)
                )
                await self.session.execute(stmt)
        except Exception as e:
            logging.error(f"notification_repo.delete_notification error {action_id}: {e}")


    async def set_sent_state(self, id: int):
        try:
            async with self.session.begin():
                stmt = (
                    update(Notification)
                    .where(Notification.id == id)
                    .values(state=NotificationStateEnum.SENT)
                )

                await self.session.execute(stmt)
        except Exception as e:
            logging.error(f"notification_repo.set_sent_state error {id}: {e}")


    async def get_notification_by_id(self, id: int) -> Notification | None:
        try:
            async with self.session.begin():
                stmt = (
                    select(Notification)
                    .where(Notification.id == id)
                    .options(selectinload(Notification.action))
                    .limit(1)
                )
                result = await self.session.execute(stmt)
                notification = result.scalar_one_or_none()
                return notification
        except Exception as e:
            print(f"notification_repo.get_notification_by_id error {id}: {e}")
            return None
