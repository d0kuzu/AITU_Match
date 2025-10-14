from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram.callbacks.registration_callbacks import TestCallbackData, CallbackData, HeldOutCallbackData, \
    HeldOutCallbackDayValues, HeldOutCallbackEmotionsValues, HeldOutCallbackCommentValues, HeldOutCallbackValues, \
    SurveyUsabilityValues, SurveyCallbackData, SurveyMotivationValues, SurveyRecommendationValues, \
    SurveyReachGoalValues, SurveyTestValues
from telegram.misc import texts


class Keyboards:
    @staticmethod
    def test_buttons():
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да", callback_data=TestCallbackData.yes)
        builder.button(text="❌ Нет", callback_data=TestCallbackData.no)
        builder.adjust(2)
        return builder.as_markup()
