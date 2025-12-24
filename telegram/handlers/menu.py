from aiogram.types import Message

from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.texts import TEXTS


async def show_menu(message: Message):
    await message.answer(TEXTS.welcome_texts.text_main_menu, reply_markup=ReplyKeyboards.main_menu())
