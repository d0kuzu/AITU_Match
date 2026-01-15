import json
import logging

from sqlalchemy import select, or_, and_, true, update, false
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import SexEnum, OppositeSexEnum
from database.models.action import Action
from database.models.complaint import Complaint
from database.models.profile import Profile
from database.repo.repo import Repo


class ComplaintRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create(self, target_id: int, reason: str, comment: str) -> Complaint|None:
        try:
            async with self.session.begin():
                stmt = Complaint(
                    target_id=target_id,
                    reason=reason,
                    comment=comment,
                )

                complaint = await self.session.merge(stmt)
            return complaint
        except Exception as e:
            logging.error(f"complaint_repo.create error {target_id}: {e}")
            return None