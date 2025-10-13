import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config.config import env
from database.repo import UserRepo

from services.openai import ask_question
from telegram.callbacks.registration_callbacks import CallbackData
from telegram.misc import texts
from telegram.misc.keyboards import Keyboards
from telegram.misc.texts import DAILY_TASK_PROMPT, AFFIRMATION_TASK_PROMPT, held_out_day_question, survey_intro


async def generate_task(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            if not user.overdue_task:
                text: str
                if user.progress == 1:
                    continue
                elif 1 < user.progress < 7:
                    prompt = DAILY_TASK_PROMPT.format(
                        name=user.name,
                        goal=user.goals[0].goal,
                        area=user.goals[0].goal_area,
                        age=user.age,
                        motivation=user.motivation,

                        plan=user.goals[0].goal_plan,
                        day=user.progress
                    )
                    text = await ask_question(prompt)

                    await user_repo.save_overdue_task(user.user_id, text)
                else:
                    text = "Поздравляем, ты выполнил свою цель! Сегодня твой последний день по нашей программе."
                    await user_repo.describe_user_notifications(user.user_id)

                await bot.send_message(user.user_id, text, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(user.user_id, user.overdue_task, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"generate task error: {e}")
            continue

async def bot_message_affirmation(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            # key = StorageKey(bot_id=bot.id, chat_id=user.user_id, user_id=user.user_id)
            # state = FSMContext(storage=storage, key=key)

            builder = InlineKeyboardBuilder()
            builder.button(text=texts.affirmation_useful, callback_data=CallbackData.AFFIRMATION_USEFUL)
            builder.button(text=texts.affirmation_useless, callback_data=CallbackData.AFFIRMATION_USELESS)
            builder.adjust(1)

            formated_prompt = AFFIRMATION_TASK_PROMPT.format(
                name=user.name,
                goal=user.goals[0].goal,
                area=user.goals[0].goal_area,
                age=user.age,
                motivation=user.motivation,

                day=user.progress
            )
            answer = "Мотивационное сообщение\n\n" + await ask_question(formated_prompt)

            await bot.send_message(user.user_id, answer, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(e)
            continue


async def send_counter(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            if user.progress == 1:
                continue
            image = FSInputFile(f"{env.counter_path}/day{user.progress}.jpg")
            await bot.send_photo(user.user_id, image)
        except Exception as e:
            logging.error(f"counter task error: {e}")
            continue


async def send_media(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            video = FSInputFile(f"{env.media_path}/day{user.progress}.mp4")
            await bot.send_video(user.user_id, video)
        except Exception as e:
            logging.error(f"counter task error: {e}")
            continue


async def send_recommendation(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            image = FSInputFile(f"{env.recommendation_path}/day{user.progress}.jpg")
            await bot.send_photo(user.user_id, image)
        except Exception as e:
            logging.error(f"counter task error: {e}")
            continue


async def remind_task(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            if user.overdue_task:
                text = f"Напоминание о задаче. \n\n{user.overdue_task}"
                await bot.send_message(user.user_id, text)
        except Exception as e:
            logging.error(f"remind task error: {e}")
            continue


async def ask_if_held_out(bot: Bot, user_repo: UserRepo):
    users = await user_repo.get_notify_users()

    for user in users:
        try:
            if user.progress >= 7:
                await bot.send_message(user.user_id, survey_intro, reply_markup=Keyboards.end_survey())
            else:
                await bot.send_message(user.user_id, held_out_day_question, reply_markup=Keyboards.how_is_day())

                if user.progress == 1:
                    await user_repo.promote_progress(user.user_id)
        except Exception as e:
            logging.error(f"held_out task error: {e}")
            continue


async def admin_daily_report(bot: Bot, user_repo: UserRepo):
    document = await user_repo.export_users_to_excel(True)
    for admin_id in env.ADMIN_IDS:
        try:
            await bot.send_document(admin_id, document, caption="Отчёт за текущий день")
        except Exception as e:
            logging.error(f"Не удалось отправить отчет {admin_id}: {e}")
