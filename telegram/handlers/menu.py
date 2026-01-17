from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.enums import FlowEnum
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS


async def show_menu(message: Message, state: FSMContext):
    await state.update_data(flow=FlowEnum.EASY.value)
    await state.clear()
    await state.set_state(MenuStates.main_menu)
    await message.answer(TEXTS.welcome_texts.text_main_menu, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboards.main_menu(), disable_web_page_preview=True)
