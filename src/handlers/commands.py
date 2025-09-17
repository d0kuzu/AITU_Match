from pathlib import Path

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from src.states import UserRoadmap
from src.service.db_service import ServiceDB
from src.keyboards.reply import welcome_keyboard, sex_selection_horizontal_keyboard
from src.config import settings


WELCOME_TEXT = """
*Привет, студент!*   

*Aitu MATCH* - это бот для знакомств среди айтушников — находи друзей, единомышленников или даже вторую половинку!  

✨ *Что тут можно делать?*  
• Смотреть анкеты других ребят 🕵🏿‍♂️
• Найти интересных людей 🎓
• Общаться с виртуальным собеседником 🥶 

_Нажми *"Начать"*, чтобы создать свою анкету или посмотреть другие!_ 
"""


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

WELCOME_IMAGE = FSInputFile(STATIC_DIR / "bot" / "welcome.jpeg")


commands_router = Router()


@commands_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    await message.answer_photo(
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        reply_markup=welcome_keyboard(),
        parse_mode="Markdown",
    )


    if await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
        await state.set_state(UserRoadmap.main_menu)
    else:
        await state.set_state(UserRoadmap.get_token)
    # await state.set_state(StartStates.start)


@commands_router.message(Command("init"))
async def command_init(message: Message, state: FSMContext):
    """Initialize the first user (admin)"""
    if message.from_user.id != settings.ADMIN_ID:
        await message.answer("Эта команда доступна только администратору.")
        return
    
    try:
        # Check if user already exists
        if await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
            await message.answer("Пользователь уже существует!")
            return
            
        # Create first user
        invite_token = await ServiceDB.create_first_user(message.from_user.id)
        await message.answer(
            f"✅ Первый пользователь создан!\n\n"
            f"Ваш инвайт-код: `{invite_token}`\n\n"
            f"Теперь вы можете приглашать других пользователей!",
            parse_mode="Markdown"
        )
        await state.set_state(UserRoadmap.main_menu)
    except Exception as e:
        print(f"Error creating first user: {e}")
        await message.answer(f"Ошибка при создании первого пользователя: {e}")


@commands_router.message(Command("debug"))
async def command_debug(message: Message, state: FSMContext):
    """Debug command to check user status"""
    if message.from_user.id != settings.ADMIN_ID:
        await message.answer("Эта команда доступна только администратору.")
        return
    
    try:
        user = await ServiceDB.get_user_by_tgid(message.from_user.id)
        if user:
            await message.answer(
                f"🔍 Debug info:\n\n"
                f"User ID: {user.user_id}\n"
                f"TG ID: {user.tg_id}\n"
                f"Invites: {user.invites}\n"
                f"Invite Code: `{user.invite_code}`",
                parse_mode="Markdown"
            )
        else:
            await message.answer("Пользователь не найден в базе данных.")
    except Exception as e:
        print(f"Error in debug command: {e}")
        await message.answer(f"Ошибка при получении информации: {e}")
