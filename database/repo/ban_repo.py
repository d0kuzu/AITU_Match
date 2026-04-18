import logging
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database.repo.repo import Repo
from database.models.ban import Ban

class BanRepo(Repo):
    async def is_banned(self, user_id: int) -> bool:
        try:
            async with self.session.begin():
                stmt = select(Ban).where(Ban.user_id == user_id)
                result = await self.session.execute(stmt)
                ban = result.scalar_one_or_none()
                return ban is not None
        except Exception as e:
            logging.error(f"BanRepo.is_banned error {user_id}: {e}")
            return False

    async def add_ban(self, user_id: int):
        try:
            async with self.session.begin():
                stmt = pg_insert(Ban).values(user_id=user_id).on_conflict_do_nothing()
                await self.session.execute(stmt)
            logging.info(f"User {user_id} added to bans")
        except Exception as e:
            logging.error(f"BanRepo.add_ban error {user_id}: {e}")
