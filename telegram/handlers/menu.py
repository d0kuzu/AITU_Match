from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram.filters.registration import RegisteredFilter
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(RegisteredFilter())
router.callback_query.filter(RegisteredFilter())

async def show_menu(message: Message):
    await message.answer(TEXTS.welcome_texts.text_main_menu, reply_markup=ReplyKeyboards.main_menu())
