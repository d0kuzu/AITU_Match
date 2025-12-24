from datetime import datetime, date
from io import BytesIO

from aiogram.types import BufferedInputFile
from sqlalchemy.dialects.postgresql import insert as pginsert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert, func, exists
import logging
from typing import Any, Dict

from sqlalchemy.orm import selectinload

from database.repo.repo import Repo
from database.models import *
import pandas as pd


class UserRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def is_exist(self, user_id: int) -> bool:
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user is not None
        except Exception as e:
            logging.error(f"user_repo.is_exist error {user_id}: {e}")
            return False


    async def is_user_exist_by_barcode(self, barcode: str) -> bool:
        try:
            stmt = select(User).where(User.barcode == barcode)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            return user is not None
        except Exception as e:
            logging.error(f"user_repo.is_exist_by_barcode error {barcode}: {e}")
            return False


    async def create(self, user_id: int, barcode) -> bool:
        try:
            async with self.session.begin():
                user = User(
                    user_id=user_id,
                    barcode=barcode
                )

                await self.session.merge(user)
            logging.info(f"User ({user_id}) saved")
            return True
        except Exception as e:
            logging.error(f"user_repo.create error {user_id}: {e}")
            return False
