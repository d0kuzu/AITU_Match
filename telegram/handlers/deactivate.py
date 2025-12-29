import asyncio

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database.repo import Repos
from telegram.handlers.menu import show_menu
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS

router = Router()

@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.want_deactivate)
async def deactivation(message: Message, state: FSMContext, repos: Repos):
    await repos.profile.set_is_active(message.from_user.id, False)

    await state.set_state(MenuStates.deactivated)
    await message.answer(TEXTS.menu_texts.say_will_wait, reply_markup=ReplyKeyboards.activate())


@router.message(MenuStates.deactivated, F.text==TEXTS.menu_texts.activate)
async def ask_activation(message: Message, state: FSMContext, repos: Repos):
    await repos.profile.set_is_active(message.from_user.id, True)

    await message.answer(TEXTS.menu_texts.welcome_back, reply_markup=ReplyKeyboardRemove())

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(1)

    await state.set_state(MenuStates.main_menu)
    await show_menu(message, state)


@router.message(MenuStates.deactivated)
async def ask_activation(message: Message):
    await message.answer(TEXTS.menu_texts.ask_activate)
