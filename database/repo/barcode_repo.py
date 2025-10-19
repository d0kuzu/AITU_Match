import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Barcode
from database.repo.repo import Repo


class BarcodeRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def is_exist(self, code: int) -> bool:
        try:
            stmt = (
                select(Barcode)
                    .where(Barcode.code == code,
                           Barcode.user_id.is_(None))
            )
            result = await self.session.execute(stmt)
            barcode = result.scalar_one_or_none()
            return barcode is not None
        except Exception as e:
            logging.error(f"barcode_repo.is_exist error: {e}")
            return False