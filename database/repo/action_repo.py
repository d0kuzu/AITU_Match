import logging

from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import ActionEnum
from database.models.action import Action
from database.repo.repo import Repo


class ActionRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create_action(self, user_id: int, target_id: int, action: ActionEnum) -> int | None:
        try:
            async with self.session.begin():
                stmt = Action(
                    user_id=user_id,
                    target_id=target_id,
                    action_type=action,
                )

                result = await self.session.merge(stmt)
            return result.id
        except Exception as e:
            logging.error(f"action_repo.create_action {action}: {e}")
            return None
