from aiogram import Router, F
from aiogram.types import Message

from database.repo import Repos
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS

router = Router()

@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.want_deactivate)
async def deactivation(message: Message, repos: Repos):
    await repos.profile.deactivate_profile(message.from_user.id)

    await message.answer(TEXTS.menu_texts.say_will_wait)