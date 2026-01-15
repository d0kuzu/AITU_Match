from enum import Enum


class SexEnum(Enum):
    MALE = "male"
    FEMALE = "female"

class OppositeSexEnum(Enum):
    MALE = "male"
    FEMALE = "female"
    BOTH = "both"

class ActionEnum(Enum):
    like = "like"
    skip = "skip"
    message = "message"
    complain = "complain"

class ActionStatusEnum(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class FlowEnum(Enum):
    HARD = "hard"
    EASY = "easy"

class NotificationStateEnum(Enum):
    WAITING = "waiting"
    SENT = "sent"

class UniEnum(Enum):  # synced with const.specializations
    SE = "SE"
    MT = "MT"
    CB = "CB"
    BDA = "BDA"
    MCS = "MCS"
    BDH = "BDH"
    CS = "CS"
    SST = "SST"
    ST = "ST"
    DT = "DT"
    DPA = "DPA"
    AB = "AB"
    IE = "IE"
    IM = "IM"
    DTNPE = "DTNPE"
    IIT = "IIT"
    EE = "EE"
