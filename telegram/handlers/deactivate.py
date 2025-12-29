from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.repo import Repos
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS

router = Router()

@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.want_deactivate)
async def deactivation(message: Message, state: FSMContext, repos: Repos):
    await repos.profile.deactivate_profile(message.from_user.id)

    await state.set_state(MenuStates.deactivated)
    await message.answer(TEXTS.menu_texts.say_will_wait, reply_markup=ReplyKeyboards.activate())


@router.message(MenuStates.deactivated)
async def ask_activation(message: Message):
    await message.answer(TEXTS.menu_texts.ask_activate)