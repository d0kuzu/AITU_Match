import asyncio
import logging

from aiogram import Router, Bot
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from database.repo import UserRepo
from telegram.filters.role import AdminFilter
from telegram.misc import texts
from telegram.misc.keyboards import Keyboards
from telegram.misc.states import QuestionState

router = Router()
router.message.filter(AdminFilter())

@router.message(Command("report"))
async def report(message: Message, user_repo: UserRepo):
    document = await user_repo.export_users_to_excel()

    await message.bot.send_document(message.from_user.id, document, caption="Общий отчет")

@router.message(Command("question"))
async def question(message: Message, state: FSMContext, user_repo: UserRepo):
    user_count, user_count_error = await extra_survey_start(message.bot, state.storage, user_repo)
    all_user = user_count + user_count_error
    await message.answer(f"Отправленно всем пользователям \n\nУспешно отправлено: {user_count} \nНеудалось отправить: {user_count_error} \nВсего: {all_user}")


async def extra_survey_start(bot: Bot, storage: MemoryStorage, user_repo: UserRepo) -> tuple[int, int]:
    users = await user_repo.get_notify_users()
    user_count = 0
    user_count_error = 0
    for user in users:
        try:
            if user.should_notify:
                await bot.send_message(user.user_id, texts.survey_intro)
                await bot.send_chat_action(user.user_id, ChatAction.TYPING)
                await asyncio.sleep(3)
                await bot.send_message(user.user_id, texts.survey_usability, reply_markup=Keyboards.survey_usability())
                user_count += 1
        except Exception as e:
            logging.error(e)
            user_count_error += 1
            continue
    return user_count, user_count_error