from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from telegram.callbacks.registration_callbacks import TestCallbackData, CallbackData, HeldOutCallbackData, \
    HeldOutCallbackDayValues, HeldOutCallbackEmotionsValues, HeldOutCallbackCommentValues, HeldOutCallbackValues, \
    SurveyUsabilityValues, SurveyCallbackData, SurveyMotivationValues, SurveyRecommendationValues, \
    SurveyReachGoalValues, SurveyTestValues
from telegram.misc import texts
from telegram.misc.texts import TEXTS


class InlineKeyboards:
    pass

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

    @staticmethod
    def main_menu():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.menu_texts.search_profiles_text)
        builder.button(text=TEXTS.menu_texts.edit_profile_text)
        builder.button(text=TEXTS.menu_texts.go_to_deepseek_text)
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def profiles_search_actions():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.search_profiles_texts.like)
        builder.button(text=TEXTS.search_profiles_texts.message)
        builder.button(text=TEXTS.search_profiles_texts.skip)
        builder.button(text=TEXTS.search_profiles_texts.leave)
        builder.adjust(3)
        return builder.as_markup()

    @staticmethod
    def view_who_liked():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.search_profiles_texts.see_who_liked)
        builder.adjust(1)
        return builder.as_markup()
