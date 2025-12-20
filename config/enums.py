from enum import Enum


class SexEnum(Enum):
    MALE = "male"
    FEMALE = "female"

class UniEnum(Enum): # TODO: sinc with const.specializations
    SE = "SE"
    CS = "CS"

class ActionEnum(Enum):
    like = "like"
    skip = "skip"
    message = "message"
