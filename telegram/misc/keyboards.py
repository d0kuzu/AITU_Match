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


    @staticmethod
    def how_is_day():
        builder = InlineKeyboardBuilder()
        builder.button(text="Хороший день", callback_data=HeldOutCallbackData(value=HeldOutCallbackDayValues.great.value).pack())
        builder.button(text="Плохой день", callback_data=HeldOutCallbackData(value=HeldOutCallbackDayValues.bad.value).pack())
        builder.button(text="Обычный день", callback_data=HeldOutCallbackData(value=HeldOutCallbackDayValues.usual.value).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def emotions_of_day(selected: list[str]):
        builder = InlineKeyboardBuilder()
        for emotion in HeldOutCallbackEmotionsValues:
            text = ("✅ " if emotion.value in selected else "") + emotion.value
            builder.button(text=text, callback_data=HeldOutCallbackData(value=emotion.value).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def leave_comment():
        builder = InlineKeyboardBuilder()
        builder.button(text="Да", callback_data=HeldOutCallbackData(value=HeldOutCallbackCommentValues.yes).pack())
        builder.button(text="Нет", callback_data=HeldOutCallbackData(value=HeldOutCallbackCommentValues.no).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def is_held_out():
        builder = InlineKeyboardBuilder()
        builder.button(text="Да", callback_data=HeldOutCallbackData(value=HeldOutCallbackValues.yes).pack())
        builder.button(text="Нет", callback_data=HeldOutCallbackData(value=HeldOutCallbackValues.no).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def end_survey():
        builder = InlineKeyboardBuilder()
        builder.button(text=texts.survey_command, callback_data=CallbackData.START_SURVEY)
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def survey_usability():
        builder = InlineKeyboardBuilder()
        for value in SurveyUsabilityValues:
            builder.button(text=value.value, callback_data=SurveyCallbackData(value=value.name).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def survey_motivation():
        builder = InlineKeyboardBuilder()
        for value in SurveyMotivationValues:
            builder.button(text=value.value, callback_data=SurveyCallbackData(value=value.name).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def survey_recommendation():
        builder = InlineKeyboardBuilder()
        for value in SurveyRecommendationValues:
            builder.button(text=value.value, callback_data=SurveyCallbackData(value=value.name).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def survey_reach_goal():
        builder = InlineKeyboardBuilder()
        for value in SurveyReachGoalValues:
            builder.button(text=value.value, callback_data=SurveyCallbackData(value=value.name).pack())
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def survey_test():
        builder = InlineKeyboardBuilder()
        for value in SurveyTestValues:
            builder.button(text=value.value, callback_data=SurveyCallbackData(value=value.name).pack())
        builder.adjust(1)
        return builder.as_markup()
