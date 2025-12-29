import json
import logging

from sqlalchemy import select, or_, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import SexEnum, OppositeSexEnum
from database.models.action import Action
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
                    sex=SexEnum(user_data["sex"]),
                    opposite_sex=OppositeSexEnum(user_data["opposite_sex"]),
                    uni=user_data["uni"],
                    description=user_data["description"],
                    s3_path=json.dumps(s3paths),
                )

                profile = await self.session.merge(stmt)
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


    async def get_sex_info(self, user_id: int) -> tuple[SexEnum, OppositeSexEnum] | None:
        try:
            async with self.session.begin():
                stmt = (
                    select(Profile.sex, Profile.opposite_sex)
                    .where(Profile.user_id == user_id)
                ).limit(1)

                result = await self.session.execute(stmt)
                row = result.one_or_none()

                return row
        except Exception as e:
            print(f"profile_repo.get_sex_info error {user_id}: {e}")


    async def search_random_user(self, user_id: int, sex: SexEnum, opposite_sex: OppositeSexEnum) -> Profile|None:
        try:
            async with self.session.begin():
                sex = OppositeSexEnum(sex.value)
                opposite_sex = SexEnum(opposite_sex.value)
                subq = (
                    select(Action.target_id)
                    .where(
                        or_(
                            Action.user_id == user_id,
                            Action.target_id == user_id
                        )
                    )
                )
                stmt = (
                    select(Profile)
                    .where(
                        Profile.user_id.notin_(subq),
                        Profile.user_id != user_id,
                        (Profile.sex == opposite_sex) if opposite_sex != OppositeSexEnum.BOTH else true(),
                        or_(Profile.opposite_sex == OppositeSexEnum.BOTH, Profile.opposite_sex == sex)
                    )
                    .limit(1)
                )

                result = await self.session.execute(stmt)
                profile = result.scalar_one_or_none()

                return profile
        except Exception as e:
            print(f"profile_repo.search_random_user error {user_id}: {e}")


    async def save_profile(self, user_id: int, data: dict):
        try:
            async with self.session.begin():
                profile = await self.session.get(Profile, user_id)

                if data.get("name") is not None:
                    profile.name = data["name"]
                if data.get("age") is not None:
                    profile.age = data["age"]
                if data.get("description") is not None:
                    profile.description = data["description"]


                if data.get("sex") is not None:
                    profile.sex = data["sex"]
                if data.get("opposite_sex") is not None:
                    profile.opposite_sex = data["opposite_sex"]
                if data.get("uni") is not None:
                    profile.uni = data["uni"]
            return
        except Exception as e:
            logging.error(f"profile_repo.save_profile error {user_id}: {e}")
