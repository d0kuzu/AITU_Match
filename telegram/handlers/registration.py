import asyncio
import logging

from aiogram import Router, F
from aiogram.enums import ChatAction, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.config import env
from database.repo import UserRepo
from telegram.callbacks.registration_callbacks import CallbackData, LIFE_AREAS, HeldOutCallbackData, \
    HeldOutCallbackDayValues, HeldOutCallbackEmotionsValues, HeldOutCallbackCommentValues, HeldOutCallbackValues, \
    SurveyCallbackData, SurveyUsabilityValues, SurveyMotivationValues, SurveyRecommendationValues, \
    SurveyReachGoalValues, SurveyTestValues
from services.openai import generate_goal_plan, ask_question
from telegram.misc import texts
from telegram.misc.keyboards import Keyboards
from telegram.misc.states import RegisterState, GoalState, SurveyState, RestartState, QuestionState
from telegram.misc.texts import start_message, \
    registration_end_message, held_out_yes, held_out_no, \
    held_out_emotions_question, held_out_comment_question, held_out_question, GOAL_CORRECTION_PROMPT, \
    before_registration
from urllib.parse import parse_qs

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext, user_repo: UserRepo):
    is_registered, has_goal = await user_repo.check_user(message.from_user.id)

    if not is_registered:
        raw_args = message.text.split(maxsplit=1)

        if len(raw_args) > 1:
            deep_link = raw_args[1]
            try:
                parsed = parse_qs(deep_link)
                utm_data = {k: v[0] for k, v in parsed.items()}
                await user_repo.set_user_utm(message.from_user.id, utm_data)
            except Exception as e:
                logging.error("Ошибка при разборе UTM:", e)

        await message.answer(start_message)

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(2)

        await message.answer(before_registration)

        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(2)

        await state.set_state(RegisterState.wait_age)
        await message.answer("Введите ваш возраст (числом):")
    elif not has_goal:
        await start_goal_planning(message, state)
    else:
        pass


@router.message(RegisterState.wait_age, F.text.isdigit())
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    builder = InlineKeyboardBuilder()
    builder.button(text="Наркотики", callback_data="addiction_drugs")
    builder.button(text="Алкоголь", callback_data="addiction_alcohol")
    builder.button(text="Игромания", callback_data="addiction_gambling")
    builder.button(text="Другое", callback_data="addiction_other")
    builder.adjust(2)
    await state.set_state(RegisterState.wait_addiction)
    await message.answer("Выберите тип зависимости:", reply_markup=builder.as_markup())


@router.callback_query(RegisterState.wait_addiction)
async def process_addiction(callback: CallbackQuery, state: FSMContext):
    addiction_type = callback.data.split("_")[1]
    if addiction_type == "other":
        await state.set_state(RegisterState.wait_addiction_other)
        await callback.message.answer("Введите ваш тип зависимости:")
    else:
        await state.update_data(addiction=addiction_type)
        await state.set_state(RegisterState.wait_name)
        await callback.message.answer("Как я могу к вам обращаться?")
    await callback.message.edit_reply_markup(None)


@router.message(RegisterState.wait_addiction_other)
async def process_addiction_other(message: Message, state: FSMContext):
    await state.update_data(addiction=message.text)
    await state.set_state(RegisterState.wait_name)
    await message.answer("Как я могу к вам обращаться?")


@router.message(RegisterState.wait_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegisterState.wait_motivation)
    await message.answer("Что является главной мотивацией для тебя в борьбе с зависимостью")


@router.message(RegisterState.wait_motivation)
async def process_motivation(message: Message, state: FSMContext, user_repo: UserRepo):
    await state.update_data(motivation=message.text)
    user_data = await state.get_data()
    await user_repo.save_user_data(message.from_user.id, user_data)

    await message.answer(registration_end_message)

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(10)

    await start_goal_planning(message, state)


async def start_goal_planning(message: Message, state: FSMContext):
    await state.set_state(GoalState.wait_area_selection)
    builder = InlineKeyboardBuilder()
    builder.button(text="Физическое здоровье", callback_data=CallbackData.AREA_PHYSICAL)
    builder.button(text="Карьера или учёба", callback_data=CallbackData.AREA_CAREER)
    builder.button(text="Отношения с близкими", callback_data=CallbackData.AREA_RELATIONSHIPS)
    builder.button(text="Духовный рост", callback_data=CallbackData.AREA_SPIRITUAL)
    builder.adjust(2)
    await message.answer(texts.goal_explanation, reply_markup=builder.as_markup())


@router.callback_query(GoalState.wait_area_selection)
async def process_area_selection(callback: CallbackQuery, state: FSMContext):
    area = callback.data
    await state.update_data(goal_area=LIFE_AREAS.get(area))
    await state.update_data(qa=[texts.goal_input])
    await state.set_state(GoalState.wait_goal_input)
    await callback.message.answer(texts.goal_input)
    await callback.message.edit_reply_markup(None)


@router.message(GoalState.wait_goal_input)
async def process_goal_input(message: Message, state: FSMContext):
    data = await state.get_data()
    qa = data.get("qa")
    qa[-1] += " Ответ: " + message.text

    question = await goal_correction(qa, data.get("goal_area", ""), data.get("motivation", ""))

    if question and len(qa) < 3:
        await message.answer(question, parse_mode=ParseMode.HTML)
        qa.append(question)
        await state.update_data(qa=qa)
    else:
        await state.update_data(goal=", \n".join(qa))
        await message.answer("Генерирую твой персональный план по достижению цели. Это может занять некоторое время")
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        user_data = await state.get_data()
        plan = await generate_goal_plan(user_data)
        await state.update_data(goal_plan=plan)

        plan_text = format_plan(plan)
        builder = InlineKeyboardBuilder()

        text = texts.plan_ready + "\n\n"
        if not "ошибка" in plan_text.lower():
            builder.button(text="Согласовать", callback_data=CallbackData.CONFIRM_PLAN)
        else:
            text = ""
            plan_text = "Мне не удалось создать для вас план, т.к. не понял ваших целей, заполните их еще раз."
        builder.button(text="Изменить", callback_data=CallbackData.EDIT_PLAN)
        await state.set_state(GoalState.wait_plan_confirmation)
        text += plan_text
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


async def goal_correction(qa, goal_area, motivation) -> str:
    prompt = GOAL_CORRECTION_PROMPT.format(qa=qa, area=goal_area, motivation=motivation)
    answer = await ask_question(prompt)
    return answer if answer.lower().find("goal completed") == -1 else ""


@router.callback_query(GoalState.wait_plan_confirmation, F.data == CallbackData.CONFIRM_PLAN)
async def confirm_plan(callback: CallbackQuery, state: FSMContext, user_repo: UserRepo):
    await callback.message.edit_reply_markup(None)
    user_data = await state.get_data()
    await user_repo.save_user_goal(callback.from_user.id, {
        "goal": user_data.get("goal"),
        "goal_area": user_data.get("goal_area"),
        "goal_plan": user_data.get("goal_plan")
    })
    await user_repo.subscribe_user_notifications(callback.from_user.id)


    await state.clear()
    await callback.message.answer(texts.plan_confirmed)

    await callback.message.bot.send_chat_action(callback.message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(5)

    image = FSInputFile(f"{env.counter_path}/day1.jpg")
    await callback.message.answer_photo(image)

    await callback.message.bot.send_chat_action(callback.message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(5)

    text = "Поздравляем, ты сделал на сегодня самое главное – расписал путь к своей цели"
    await callback.message.answer(text)


@router.callback_query(GoalState.wait_plan_confirmation, F.data == CallbackData.EDIT_PLAN)
async def edit_plan(callback: CallbackQuery, state: FSMContext):
    await state.update_data(qa=[texts.goal_input])
    await state.set_state(GoalState.wait_goal_input)
    await callback.message.answer("Давайте скорректируем вашу цель. Опишите её заново:")
    await callback.message.edit_reply_markup(None)


@router.callback_query(lambda callback: callback.data in ["affirmation_useful", "affirmation_useless"])
async def process_affirmation_feedback(callback: CallbackQuery, user_repo: UserRepo):
    feedback = callback.data
    await user_repo.save_user_affirmation(callback.from_user.id, feedback, callback.message.text)
    await callback.message.edit_reply_markup(None)
    await callback.answer("Спасибо за ваш отзыв!")
    await callback.message.answer("Ваш отзыв сохранен.")


@router.message(SurveyState.wait_features)
async def process_user_info(message: Message, state: FSMContext):
    await state.update_data(features=message.text)
    await state.set_state(SurveyState.wait_bad_features)
    await message.answer(texts.survey_bad_features)


@router.message(SurveyState.wait_bad_features)
async def process_user_info(message: Message, state: FSMContext):
    await state.update_data(bad_features=message.text)
    await state.set_state(None)
    await message.answer(texts.survey_motivation, reply_markup=Keyboards.survey_motivation())


@router.message(SurveyState.wait_new_features)
async def process_user_info(message: Message, state: FSMContext):
    await state.update_data(new_features=message.text)
    await state.set_state(SurveyState.wait_cost)
    await message.answer(texts.survey_cost)


@router.message(SurveyState.wait_cost)
async def process_user_info(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await state.set_state(None)
    await message.answer(texts.survey_test, reply_markup=Keyboards.survey_test())


@router.callback_query(SurveyCallbackData.filter())
async def survey_callback_data_filter(callback: CallbackQuery, callback_data: SurveyCallbackData, state: FSMContext, user_repo: UserRepo):
    await callback.message.edit_reply_markup(None)
    value = callback_data.value
    print(value)

    if value in SurveyUsabilityValues.__members__:
        await state.clear()
        value = SurveyUsabilityValues[value].value
        await state.update_data(usability=value)
        await state.set_state(SurveyState.wait_features)
        await callback.message.answer(texts.survey_features)

    elif value in SurveyMotivationValues.__members__:
        value = SurveyMotivationValues[value].value
        await state.update_data(motivation=value)
        await callback.message.answer(texts.survey_recommendation, reply_markup=Keyboards.survey_recommendation())

    elif value in SurveyRecommendationValues.__members__:
        value = SurveyRecommendationValues[value].value
        await state.update_data(recommendation=value)
        await callback.message.answer(texts.survey_reach_goal, reply_markup=Keyboards.survey_reach_goal())

    elif value in SurveyReachGoalValues.__members__:
        value = SurveyReachGoalValues[value].value
        await state.update_data(reach_goal=value)
        await state.set_state(SurveyState.wait_new_features)
        await callback.message.answer(texts.survey_new_features)

    elif value in SurveyTestValues.__members__:
        value = SurveyTestValues[value].value
        await state.update_data(test=value)
        data = await state.get_data()
        print(data)
        await state.clear()
        questions = {
            texts.survey_usability: data.get("usability", ""),
            texts.survey_features: data.get("features", ""),
            texts.survey_bad_features: data.get("bad_features", ""),
            texts.survey_motivation: data.get("motivation", ""),
            texts.survey_recommendation: data.get("recommendation", ""),
            texts.survey_reach_goal: data.get("reach_goal", ""),
            texts.survey_new_features: data.get("new_features", ""),
            texts.survey_cost: data.get("cost", ""),
            texts.survey_test: data.get("test", ""),
        }
        user = await user_repo.get_user(callback.from_user.id)
        text = f"Ответы на опрос пользователя {user.name}(@{callback.from_user.username}) (зависимость - {user.addiction}):\n\n"
        for question, answer in questions.items():
            text += f"{question} \nОтвет: {answer}\n"
        await callback.bot.send_message(env.survey_group, text)

    await callback.message.edit_text(callback.message.text + " Ответ: " + value)


# @router.message(Command("restart"))
# async def command_restart(message: Message, state: FSMContext):
#     await start_restart_flow(message, state)


# @router.callback_query(F.data == CallbackData.RESTART_BOT)
# async def callback_restart(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_reply_markup(None)
#     await start_restart_flow(callback.message, state)


async def start_restart_flow(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.restart_reason_change, callback_data=CallbackData.RESTART_REASON_CHANGE)
    builder.button(text=texts.restart_reason_relapse, callback_data=CallbackData.RESTART_REASON_RELAPSE)
    builder.adjust(1)
    await state.set_state(RestartState.wait_reason)
    await message.answer(texts.restart_question, reply_markup=builder.as_markup())


@router.callback_query(RestartState.wait_reason)
async def process_restart_reason(callback: CallbackQuery, state: FSMContext):
    reason = callback.data
    await state.update_data(restart_reason=reason)
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, начать заново", callback_data=CallbackData.RESTART_CONFIRM)
    builder.button(text="Нет, отменить", callback_data=CallbackData.RESTART_CANCEL)
    builder.adjust(1)
    await state.set_state(RestartState.wait_confirmation)
    await callback.message.answer(texts.restart_confirmation, reply_markup=builder.as_markup())
    await callback.message.edit_reply_markup(None)


@router.callback_query(RestartState.wait_confirmation, F.data == CallbackData.RESTART_CONFIRM)
async def confirm_restart(callback: CallbackQuery, state: FSMContext, user_repo: UserRepo):
    user_data = await state.get_data()
    restart_reason = user_data.get("restart_reason")
    await state.storage.set_state(state.key, None)
    # user_repo.delete_user(callback.from_user.id)
    if restart_reason == CallbackData.RESTART_REASON_RELAPSE:
        # user_repo.add_relapsed(callback.from_user.id)
        await callback.message.answer(texts.relapse_message)
        await callback.message.answer(texts.center_recommendation)
    await state.set_state(RegisterState.wait_age)
    await callback.message.answer("Введите ваш возраст (числом):")
    await callback.message.edit_reply_markup(None)


@router.callback_query(RestartState.wait_confirmation, F.data == CallbackData.RESTART_CANCEL)
async def cancel_restart(callback: CallbackQuery, state: FSMContext):
    await state.storage.set_state(state.key, None)
    await callback.message.answer("Перезапуск отменен. Продолжаем работу с текущими данными.")
    await callback.message.edit_reply_markup(None)


def format_plan(plan: dict) -> str:
    if "error" in plan:
        return f"Произошла ошибка при создании плана: {plan.get('error')}"
    try:
        text = f"📝 <b>{plan['plan_name']}</b>\n\n"
        text += f"{plan['description']}\n\n"
        for day in plan.get("days", []):
            text += f"<b>День {day['day']}: {day['title']}</b>\n"
            text += f"{day['description']}\n"
            text += f"{day['task']}\n\n"
        return text
    except Exception as e:
        print(f"Ошибка форматирования плана: {str(e)}\n\nИсходный план: {plan}")
        return f"Ошибка форматирования плана"


# @router.message(Command("advice"))
# async def advice_question(message: Message, state: FSMContext):
#     await state.set_state(AdviceState.wait_question)
#
#     await message.answer("Напишите по какому вопросу вам требуется совет?")
#
#
# @router.message(AdviceState.wait_question)
# async def advice_answer(message: Message, state: FSMContext, user_repo: UserRepo):
#     await state.storage.set_state(state.key, None)
#     user = await user_repo.get_user_with_goals(message.from_user.id)
#     if not user:
#         await message.answer("Для начала вам нужно пройти регистрацию. \nДля этого используйте команду /start")
#         return
#     elif len(user.goals) == 0:
#         await message.answer("Вам нужно заполнить ваши цели. \nДля этого используйте команду /start")
#         return
#     delta = datetime.now() - user.last_use
#     days_difference = delta.days
#
#     prompt = ADVICE_PROMPT.format(
#         goal=user.goals[0].goal,
#         area=user.goals[0].goal_area,
#         age=user.age,
#         experience=user.experience,
#         motivation=user.motivation,
#         day=days_difference,
#         advice=message.text
#     )
#     answer = await ask_question(prompt)
#
#     await message.answer(answer, parse_mode=ParseMode.HTML)
#
#
# @router.message(Command("motivation"))
# async def get_motivation_handler(message: Message, user_repo: UserRepo):
#     await get_motivation(message, user_repo, message.from_user.id)
#
# async def get_motivation(message: Message, user_repo: UserRepo, user_id: int):
#     user = await user_repo.get_user_with_goals(user_id)
#     if not user:
#         await message.answer("Для начала вам нужно пройти регистрацию. \nДля этого используйте команду /start")
#         return
#     elif len(user.goals) == 0:
#         await message.answer("Вам нужно заполнить ваши цели. \nДля этого используйте команду /start")
#         return
#     delta = datetime.now() - user.last_use
#     days_difference = delta.days
#
#     prompt = MOTIVATION_PROMPT.format(
#         goal=user.goals[0].goal,
#         area=user.goals[0].goal_area,
#         age=user.age,
#         experience=user.experience,
#         motivation=user.motivation,
#         day=days_difference,
#     )
#     answer = await ask_question(prompt)
#
#     await message.answer(f"\n\n{answer}", parse_mode=ParseMode.HTML)


@router.message(QuestionState.wait_answer)
async def get_answer_of_daily_question(message: Message, state: FSMContext, user_repo: UserRepo):
    data = await state.get_data()
    await state.clear()

    await user_repo.load_user_daily_answer(data.get("daily_question"), message.text, message.from_user.id)
    await message.answer("Ваш ответ записан")


@router.message(QuestionState.wait_answer_extra_survey)
async def get_answer_of_extra_survey(message: Message, state: FSMContext, user_repo: UserRepo):
    await state.clear()

    await user_repo.load_user_extra_survey_answer(message.text, message.from_user.id)
    await message.answer("Благодарю за ответ!")


@router.callback_query(HeldOutCallbackData.filter())
async def held_out_day_great(callback: CallbackQuery, callback_data: HeldOutCallbackData, state: FSMContext, user_repo: UserRepo):
    await callback.message.edit_reply_markup(None)
    value = callback_data.value
    user_id = callback.from_user.id

    if value in HeldOutCallbackDayValues._value2member_map_:
        progress = await user_repo.get_progress(user_id)
        await user_repo.save_held_out_how_is_day_answer(user_id, value, progress)

        await callback.message.answer(held_out_emotions_question, reply_markup=Keyboards.emotions_of_day([]))

    elif value in HeldOutCallbackEmotionsValues._value2member_map_:
        data = await state.get_data()
        selected_emotions = data.get("selected_emotions", [])
        if value == HeldOutCallbackEmotionsValues.emotions_submit:
            await state.clear()
            await user_repo.save_held_out_emotions_answer(user_id, selected_emotions)

            await callback.message.answer(held_out_comment_question, reply_markup=Keyboards.leave_comment())
            return

        if value in selected_emotions:
            selected_emotions.remove(value)
        else:
            selected_emotions.append(value)
        await state.update_data(selected_emotions=selected_emotions)

        await callback.message.edit_reply_markup(reply_markup=Keyboards.emotions_of_day(selected_emotions))

    elif value == HeldOutCallbackCommentValues.yes:
        await state.set_state(QuestionState.wait_answer_held_out_comment)
        await callback.message.answer("Напишите пару предложений о том как прошел ваш день")
    elif value == HeldOutCallbackCommentValues.no:
        await user_repo.save_held_out_comment_answer(user_id, "Отсутствует")
        await is_held_out(callback.message, user_repo, callback.from_user.id)

    elif value == HeldOutCallbackValues.yes:
        await user_repo.promote_progress(callback.from_user.id)
        await user_repo.save_held_out_task_answer(user_id, value)
        await callback.message.answer(held_out_yes)
    elif value == HeldOutCallbackValues.no:
        await user_repo.save_held_out_task_answer(user_id, value)
        await callback.message.answer(held_out_no)


@router.message(QuestionState.wait_answer_held_out_comment)
async def get_held_out_comment(message: Message, state: FSMContext, user_repo: UserRepo):
    await state.clear()
    await user_repo.save_held_out_comment_answer(message.from_user.id, message.text)

    await is_held_out(message, user_repo, message.from_user.id)

async def is_held_out(message: Message, user_repo: UserRepo, user_id: int):
    user = await user_repo.get_user(user_id)
    if user.progress == 1:
        return
    await message.answer(held_out_question, reply_markup=Keyboards.is_held_out())
