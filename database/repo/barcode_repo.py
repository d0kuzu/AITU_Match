import logging
from typing import Any

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Barcode
from database.repo.repo import Repo


class BarcodeRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def is_exist(self, code: str) -> bool:
        try:
            async with self.session.begin():
                stmt = (
                    select(Barcode)
                        .where(Barcode.code == code)
                )
                result = await self.session.execute(stmt)
                barcode = result.scalar_one_or_none()
            return barcode is not None
        except Exception as e:
            logging.error(f"barcode_repo.is_exist error {code}: {e}")
            return False

    async def add_multiple(self, values: list[dict[str, Any]]) -> None:
        try:
            async with self.session.begin():
                stmt = (
                    insert(Barcode)
                )
                await self.session.execute(stmt, values)
        except Exception as e:
            logging.error(f"barcode_repo.add_multiple error {e}")