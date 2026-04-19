import json
import logging

from sqlalchemy import select, or_, and_, true, update, false, delete
from sqlalchemy.orm import selectinload
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

    async def get_all(self) -> list[Complaint]:
        stmt = select(Complaint).options(selectinload(Complaint.target_profile))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_all(self):
        async with self.session.begin():
            await self.session.execute(delete(Complaint))