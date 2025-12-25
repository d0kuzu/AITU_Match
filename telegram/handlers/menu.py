from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.enums import FlowEnum
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS


async def show_menu(message: Message, state: FSMContext):
    await state.update_data(flow=FlowEnum.EASY)
    await state.clear()
    await state.set_state(MenuStates.main_menu)
    await message.answer(TEXTS.welcome_texts.text_main_menu, reply_markup=ReplyKeyboards.main_menu())
