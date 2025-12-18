import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.profile import Profile
from database.repo.repo import Repo


class ProfileRepo(Repo):
    def __init__(self, session: AsyncSession):
        super().__init__(session)


    async def create(self, user_id: int, user_data: dict[str, any], s3paths: list[str]) -> Profile|None:
        try:
            async with self.session.begin():
                stmt = Profile(
                    user_id=user_id,
                    name=user_data["name"],
                    age=user_data["age"],
                    sex=user_data["sex"],
                    opposite_sex=user_data["opposite_sex"],
                    uni=user_data["uni"],
                    description=user_data["description"],
                    s3_path=json.dumps(s3paths),
                )

                profile = await self.session.merge(stmt)
            logging.info(f"Данные пользователя сохранены: {user_data}, user_id: {user_id}")
            return profile
        except Exception as e:
            logging.error(f"profile_repo.create error {user_id}: {e}")
            return None


    async def search_by_user_id(self, user_id: int) -> Profile|None:
        try:
            async with self.session.begin():
                stmt = (
                    select(Profile)
                    .where(Profile.user_id == user_id)
                )
                result = await self.session.execute(stmt)
                profile = result.scalar_one_or_none()
            return profile
        except Exception as e:
            logging.error(f"profile_repo.search_by_user_id error {user_id}: {e}")
            return None

    async def search_random_user(self, user_id: int) -> Profile|None:
        try:
            async with self.session.begin():
                subq = (
                    select(Action.action_owner).where(Action.action_owner == user_id or Action.action_target == user_id)
                )
                stmt = (
                    select(Profile)
                    .where(Profile.user_id.notin_(subq))
                    .limit(1)
                )

                result = await self.session.execute(stmt)
                profile = result.scalar_one_or_none()

                return profile
        except Exception as e:
            print(f"profile_repo.search_random_user error {user_id}: {e}")

