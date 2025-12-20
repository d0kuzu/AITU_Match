from .action_repo import ActionRepo
from .barcode_repo import BarcodeRepo
from .notification_repo import NotificationRepo
from .profile_repo import ProfileRepo
from .user_repo import UserRepo

class Repos:
    def __init__(self, session):
        self.user = UserRepo(session)
        self.profile = ProfileRepo(session)
        self.barcode = BarcodeRepo(session)
        self.action = ActionRepo(session)
        self.notification = NotificationRepo(session)