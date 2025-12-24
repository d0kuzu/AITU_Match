from enum import Enum


class SexEnum(Enum):
    MALE = "male"
    FEMALE = "female"

class OppositeSexEnum(Enum):
    MALE = "male"
    FEMALE = "female"
    BOTH = "both"

class UniEnum(Enum): # TODO: sinc with const.specializations
    SE = "SE"
    CS = "CS"

class ActionEnum(Enum):
    like = "like"
    skip = "skip"
    message = "message"

class FlowEnum(Enum):
    HARD = "hard"
    EASY = "easy"

class NotificationStateEnum(Enum):
    WAITING = "waiting"
    SENT = "sent"
