from enum import Enum
from typing import Dict

from aiogram.filters.callback_data import CallbackData


class SurveyCallbackData(CallbackData, prefix="survey"):
    value: str


class SurveyUsabilityValues(str, Enum):
    usability_very_negative = "Совсем не полезен"
    usability_negative = "Скорее не полезен"
    usability_neutral = "Нейтрально"
    usability_positive = "Скорее полезен"
    usability_very_positive = "Очень полезен"


class SurveyMotivationValues(str, Enum):
    motivation_yes = "Да "
    motivation_no = "Нет "


class SurveyRecommendationValues(str, Enum):
    recommendation_very_positive = "Да, уже порекомендовал(а)"
    recommendation_positive = "Да, порекомендую"
    recommendation_neutral = "Возможно"
    recommendation_negative = "Скорее нет"
    recommendation_very_negative = "Нет"


class SurveyReachGoalValues(str, Enum):
    reach_goal_positive = "Да, на 100%"
    reach_goal_neutral = "Частично"
    reach_goal_negative = "Не удалось"


class SurveyTestValues(str, Enum):
    test_positive = "Да"
    test_negative = "Нет"
    test_neutral = "Возможно, расскажите подробнее"



class HeldOutCallbackData(CallbackData, prefix="held"):
    value: str


class HeldOutCallbackDayValues(str, Enum):
    great = "хорошо"
    usual = "обычно"
    bad = "плохо"


class HeldOutCallbackEmotionsValues(str, Enum):
    happy = "радость"
    sad = "грусть"
    angry = "злость"
    anxious = "тревога"
    relaxed = "спокойствие"
    proud = "гордость"
    tired = "усталость"
    inspired = "вдохновение"
    emotions_submit = "Подтвердить"


class HeldOutCallbackCommentValues:
    yes = "Commentда"
    no = "Commentнет"


class HeldOutCallbackValues():
    yes = "да"
    no = "нет"


class TestCallbackData:
    yes = "да"
    no = "нет"

class CallbackData:
    AREA_PHYSICAL = "area_physical"
    AREA_CAREER = "area_career"
    AREA_RELATIONSHIPS = "area_relationships"
    AREA_SPIRITUAL = "area_spiritual"
    CONFIRM_PLAN = "confirm_plan"
    EDIT_PLAN = "edit_plan"
    START_SURVEY = "start_survey"
    RESTART_BOT = "restart_bot"
    RESTART_REASON_CHANGE = "restart_reason_change"
    RESTART_REASON_RELAPSE = "restart_reason_relapse"
    RESTART_CONFIRM = "restart_confirm"
    RESTART_CANCEL = "restart_cancel"
    SETTINGS_SAVE = "settings_save"
    SETTINGS_CANCEL = "settings_cancel"
    AFFIRMATION_USEFUL = "affirmation_useful"
    AFFIRMATION_USELESS = "affirmation_useless"

LIFE_AREAS: Dict[str, str] = {
    "area_physical": "Физическое здоровье",
    "area_career": "Карьера или учёба",
    "area_relationships": "Отношения с близкими",
    "area_spiritual": "Духовный рост"
}