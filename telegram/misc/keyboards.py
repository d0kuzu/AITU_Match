from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from telegram.callbacks.registration_callbacks import TestCallbackData, CallbackData, HeldOutCallbackData, \
    HeldOutCallbackDayValues, HeldOutCallbackEmotionsValues, HeldOutCallbackCommentValues, HeldOutCallbackValues, \
    SurveyUsabilityValues, SurveyCallbackData, SurveyMotivationValues, SurveyRecommendationValues, \
    SurveyReachGoalValues, SurveyTestValues
from telegram.misc import texts
from telegram.misc.texts import TEXTS


class InlineKeyboards:
    @staticmethod
    def test_buttons():
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Да", callback_data=TestCallbackData.yes)
        builder.button(text="❌ Нет", callback_data=TestCallbackData.no)
        builder.adjust(2)
        return builder.as_markup()


class ReplyKeyboards:
    @staticmethod
    def welcome_keyboard():
        builder = ReplyKeyboardBuilder()
        builder.button(text="Начать")
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def choose_sex():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_sex_male)
        builder.button(text=TEXTS.profile_texts.profile_create_sex_female)
        builder.adjust(2)
        return builder.as_markup()

    @staticmethod
    def choose_opposite_sex():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_males)
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_females)
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_both)
        builder.adjust(3)
        return builder.as_markup()

    @staticmethod
    def save_photos():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_photo_save)
        builder.adjust(1)
        return builder.as_markup()
