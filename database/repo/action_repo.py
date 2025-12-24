import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import ActionEnum, ActionStatusEnum
from database.models.action import Action
from database.repo.repo import Repo


class ActionRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create_action(self, user_id: int, target_id: int, action: ActionEnum, message: str="") -> int | None:
        try:
            async with self.session.begin():
                stmt = Action(
                    user_id=user_id,
                    action_type=action,
                    target_id=target_id,
                    status=ActionStatusEnum.PENDING,
                    message=message
                )

                result = await self.session.merge(stmt)
            return result.id
        except Exception as e:
            logging.error(f"action_repo.create_action error {action}: {e}")
            return None


    async def change_action_status(self, action_id: int, status: ActionStatusEnum):
        try:
            async with self.session.begin():
                stmt = (
                    update(Action)
                    .where(Action.id == action_id)
                    .values(status=status)
                )
                await self.session.execute(stmt)
        except Exception as e:
            logging.error(f"action_repo.change_action_status error: {e}")

