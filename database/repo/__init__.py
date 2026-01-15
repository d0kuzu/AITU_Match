from .action_repo import ActionRepo
from .barcode_repo import BarcodeRepo
from .complaint_repo import ComplaintRepo
from .notification_repo import NotificationRepo
from .profile_repo import ProfileRepo
from .user_repo import UserRepo

class Repos:
    def __init__(self, session):
        self.user: UserRepo = UserRepo(session)
        self.profile: ProfileRepo = ProfileRepo(session)
        self.barcode: BarcodeRepo = BarcodeRepo(session)
        self.action: ActionRepo = ActionRepo(session)
        self.notification: NotificationRepo = NotificationRepo(session)
        self.complaint: ComplaintRepo = ComplaintRepo(session)