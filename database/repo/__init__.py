from sqlalchemy import delete, select
from .action_repo import ActionRepo
from .barcode_repo import BarcodeRepo
from .complaint_repo import ComplaintRepo
from .notification_repo import NotificationRepo
from .profile_repo import ProfileRepo
from .user_repo import UserRepo
from .ban_repo import BanRepo
from database.models import Profile, Action, Complaint, Notification, User

class Repos:
    def __init__(self, session):
        self.session = session
        self.user: UserRepo = UserRepo(session)
        self.profile: ProfileRepo = ProfileRepo(session)
        self.barcode: BarcodeRepo = BarcodeRepo(session)
        self.action: ActionRepo = ActionRepo(session)
        self.notification: NotificationRepo = NotificationRepo(session)
        self.complaint: ComplaintRepo = ComplaintRepo(session)
        self.ban: BanRepo = BanRepo(session)

    async def delete_user_completely(self, user_id: int):
        async with self.session.begin():
            # 1. Get all action IDs involving the user to delete related notifications
            action_ids_stmt = select(Action.id).where((Action.user_id == user_id) | (Action.target_id == user_id))
            action_ids_result = await self.session.execute(action_ids_stmt)
            action_ids = action_ids_result.scalars().all()
            
            if action_ids:
                await self.session.execute(delete(Notification).where(Notification.action_id.in_(action_ids)))
            
            # 2. Delete actions
            await self.session.execute(delete(Action).where((Action.user_id == user_id) | (Action.target_id == user_id)))
            
            # 3. Delete complaints
            await self.session.execute(delete(Complaint).where((Complaint.target_id == user_id)))
            
            # 4. Delete profile
            await self.session.execute(delete(Profile).where(Profile.user_id == user_id))
            
            # 5. Delete user
            await self.session.execute(delete(User).where(User.user_id == user_id))