from typing import List
import jwt
from random import randint 

from src.config import settings
from src.repository.queries import AsyncORM, UserORM, ProfileORM, LikeORM, BarcodesORM
from src.service.schemas import UserSchema, ProfileSchema, ProfileCreateInternalSchema, LikeSchema


class ServiceDB:
    @staticmethod
    def generate_invite_code(tg_id: int):
        return jwt.encode({'sub': str(tg_id), 'random': randint(1,1000000000)}, settings.JWT_SECRET, algorithm="HS256")

    # @staticmethod
    # async def is_valid_code(code: str):
    #     try:
    #         payload = dict(jwt.decode(code, settings.JWT_SECRET, algorithms=["HS256"]))
    #     except jwt.exceptions.InvalidTokenError as e:
    #         print(f"Invalid JWT token: {e}")
    #         return False
    #
    #     print(f"JWT payload: {payload}")
    #     inviter_tgid = payload.get("sub")
    #
    #     if inviter_tgid is None:
    #         print("No 'sub' field in JWT payload")
    #         return False
    #
    #     try:
    #         inviter_tgid = int(inviter_tgid)
    #     except (ValueError, TypeError):
    #         print(f"Invalid tg_id in JWT payload: {inviter_tgid}")
    #         return False
    #
    #     print(f"Looking for inviter with TG ID: {inviter_tgid}")
    #
    #     user_data = await UserORM.get_user_by_tgid(inviter_tgid)
    #     if user_data is None:
    #         print(f"Inviter with TG ID {inviter_tgid} not found")
    #         return False
    #
    #     user = UserSchema.model_validate(user_data)
    #     print(f"Current user data - invites: {user.invites}, invite_code: {user.invite_code}")
    #     print(f"Comparing codes - stored: '{user.invite_code}' vs provided: '{code}'")
    #
    #     if user.invite_code == code and user.invites > 0:
    #         print(f"Valid invite code found for user {inviter_tgid}")
    #         new_code = ServiceDB.generate_invite_code(inviter_tgid)
    #         print(f"Generated new code: {new_code}")
    #         success = await UserORM.update_invites_and_code_by_tgid(inviter_tgid, user.invites-1, new_code)
    #         if success:
    #             print(f"Successfully updated invites for user {inviter_tgid} - new invites: {user.invites-1}")
    #             return True
    #         else:
    #             print(f"Failed to update invites for user {inviter_tgid}")
    #             return False
    #     else:
    #         print(f"Invalid invite code - code matches: {user.invite_code == code}, invites left: {user.invites}")
    #         return False

    
    @staticmethod
    async def is_user_exist_by_tgid(tg_id: int) -> bool:
        user = await UserORM.get_user_by_tgid(tg_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def is_user_exist_by_id(user_id: int) -> bool:
        user = await UserORM.get_user_by_id(user_id)

        if user is None:
            return False
        return True

    @staticmethod
    async def is_barcode_in_base(barcode: int) -> bool:
        return await BarcodesORM.check_if_barcode_exist(barcode)

    @staticmethod
    async def is_user_exist_by_barcode(barcode: int) -> bool:
        user = await UserORM.get_user_by_barcode(barcode)

        if user is None:
            return False
        return True

    @staticmethod
    async def get_user_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await UserORM.get_user_by_tgid(tg_id)
        user = UserSchema.model_validate(user_data)
        if user is None:
            return None
        return user
    

    @staticmethod
    async def get_invite_info_by_tgid(tg_id: int) -> UserSchema | None:
        user_data = await UserORM.get_user_by_tgid(tg_id)
        if user_data is None:
            print(f"User with TG ID {tg_id} not found")
            return None
        user = UserSchema.model_validate(user_data)
        print(f"Retrieved invite info for user {tg_id}: invites={user.invites}, code={user.invite_code}")
        return (user.invites, user.invite_code)

    @staticmethod
    async def add_user(tg_id: int, barcode: int):
        try:
            await UserORM.create_user(tg_id, 3, barcode, None)
            print(f"Successfully created user {tg_id} with invite code")
        except Exception as e:
            print(f"Error creating user {tg_id}: {e}")
            raise e

    # @staticmethod
    # async def create_first_user(tg_id: int):
    #     """Create the first user (admin) with unlimited invites"""
    #     try:
    #         invite_token = ServiceDB.generate_invite_code(tg_id)
    #         await UserORM.create_user(tg_id, 999, 0, invite_token)  # 999 invites for first user
    #         print(f"Successfully created first user {tg_id} with 999 invites")
    #         return invite_token
    #     except Exception as e:
    #         print(f"Error creating first user {tg_id}: {e}")
    #         raise e


    @staticmethod
    async def is_profile_exist_by_tgid(tg_id: int) -> bool:
        profile = await ProfileORM.get_profile_by_tgid(tg_id)
        if profile is None:
            return False
        return True
    
    @staticmethod
    async def add_profile(profile_to_add: ProfileCreateInternalSchema):
        await ProfileORM.create_profile(profile_to_add)

    @staticmethod
    async def update_profile(profile_to_update: ProfileCreateInternalSchema):
        await ProfileORM.update_profile(profile_to_update)

    @staticmethod
    async def search_profile(curr_user_tgid: int) -> ProfileSchema:
        profile = await ProfileORM.get_random_profile_except_tgid(curr_user_tgid)
        return ProfileSchema.model_validate(profile) if profile else None
    
    @staticmethod
    async def get_profile_by_tgid(tgid: int) -> ProfileSchema | None:
        profile = await ProfileORM.get_profile_by_tgid(tgid)
        return ProfileSchema.model_validate(profile) if profile else None
    
    @staticmethod
    async def like_profile(liker_tgid, liked_tgid: int):
        await LikeORM.create_like(liker_tgid, liked_tgid)

    @staticmethod
    async def reject_like(liker_tgid: int, liked_tgid: int): 
        await LikeORM.delete_like(liker_tgid, liked_tgid)

    @staticmethod
    async def accept_like(liker_tgid: int, liked_tgid: int):
        await LikeORM.accept_like(liker_tgid, liked_tgid)

    @staticmethod
    async def get_pending_likes(liked_tgid: int) -> List[LikeSchema]:
        likes_data = await LikeORM.get_all_pending_likes_by_liked_tgid(liked_tgid)

        if likes_data is None:
            return None
        
        likes = [LikeSchema.model_validate(like) for like in likes_data]
            
        return likes
    
    @staticmethod
    async def get_accepted_likes(liker_tgid: int) -> List[LikeSchema]:
        likes_data = await LikeORM.get_all_accepted_likes_by_liker_tgid(liker_tgid)
        likes_data += await LikeORM.get_all_accepted_likes_by_liked_tgid(liker_tgid)

        if likes_data is None:
            return None
        
        likes = [LikeSchema.model_validate(like) for like in likes_data]
            
        return likes
    