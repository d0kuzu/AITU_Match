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
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def choose_sex():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_sex_male)
        builder.button(text=TEXTS.profile_texts.profile_create_sex_female)
        builder.adjust(2)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def choose_opposite_sex():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_males)
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_females)
        builder.button(text=TEXTS.profile_texts.profile_create_opposite_sex_both)
        builder.adjust(3)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def save_photos():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.profile_texts.profile_create_photo_save)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def main_menu():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.menu_texts.search_profiles_text)
        builder.button(text=TEXTS.menu_texts.edit_profile_text)
        builder.button(text=TEXTS.menu_texts.want_deactivate)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def profiles_search_actions():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.search_profiles_texts.like)
        builder.button(text=TEXTS.search_profiles_texts.message)
        builder.button(text=TEXTS.search_profiles_texts.skip)
        builder.button(text=TEXTS.search_profiles_texts.leave)
        builder.button(text=TEXTS.search_profiles_texts.complain)
        builder.adjust(4)
        return builder.as_markup(resize_keyboard=True)

    @staticmethod
    def view_who_liked():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.notification_texts.see_likes)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


    @staticmethod
    def view_who_liked_actions():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.search_profiles_texts.like)
        builder.button(text=TEXTS.search_profiles_texts.skip)
        builder.adjust(2)
        return builder.as_markup(resize_keyboard=True)


    @staticmethod
    def ask_what_to_edit():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.edit_profile.edit_name)
        builder.button(text=TEXTS.edit_profile.edit_age)
        builder.button(text=TEXTS.edit_profile.edit_description)
        builder.button(text=TEXTS.edit_profile.edit_images)
        builder.button(text=TEXTS.edit_profile.edit_all)
        builder.button(text=TEXTS.edit_profile.back_to_menu)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


    @staticmethod
    def activate():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.menu_texts.activate)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


    @staticmethod
    def complain_reasons():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.complain_texts.mature_content)
        builder.button(text=TEXTS.complain_texts.sell_add)
        builder.button(text=TEXTS.complain_texts.other)
        builder.button(text=TEXTS.complain_texts.back)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


    @staticmethod
    def go_back():
        builder = ReplyKeyboardBuilder()
        builder.button(text=TEXTS.complain_texts.back)
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)
