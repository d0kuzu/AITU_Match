from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from config.config import Environ
from telegram.filters.registration import RegisteredFilter
from telegram.misc.paths import PATHS
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(not RegisteredFilter())

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext, env: Environ):
    await message.answer_photo(
        photo=FSInputFile(PATHS.welcome_photo),
        caption=TEXTS.welcome_texts.welcome_text,
        reply_markup=welcome_keyboard(),
        parse_mode="Markdown",
    )

    if await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
        await state.set_state(UserRoadmap.main_menu)
    else:
        await state.set_state(UserRoadmap.get_token)
