import random

from aiogram import F
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from src.config import settings
from src.repository.queries import BarcodesORM
from src.service.db_service import ServiceDB
from src.states import SearchProfileStates, UserRoadmap, CreateProfileStates, EditProfileStates

from src.service.llm import llm_generate, llm_init_agent, llm_generate_simple

from src.keyboards.reply import (
    go_to_main_menu, go_to_check_token, 
    main_menu_keyboard, yes_or_no_keyboard,
    understand_keyboard, welcome_keyboard
) 

from src.static.text.texts import (
    text_main_menu, text_main_menu_get_back,
    text_search_profiles, text_edit_profile,
    text_show_invite_code, text_go_to_deepseek, 
    text_no, text_yes,
    text_profile_create_begin,
    text_search_profiles_start,
)


user_router = Router()


@user_router.message(UserRoadmap.start)
async def user_start(message: Message, state: FSMContext):
    pass


@user_router.message(UserRoadmap.get_token)
async def user_get_token(message: Message, state: FSMContext):
    await state.set_state(UserRoadmap.check_token)
    await message.answer(
        "Ты еще не зарегестрирован! Введи свой barcode и присоединяйся!",
        reply_markup=ReplyKeyboardRemove(),
    )


@user_router.message(UserRoadmap.check_token)
async def user_check_token(message: Message, state: FSMContext):
    if message.text and message.text.isdigit():
        if len(message.text) == 6 and await ServiceDB.is_barcode_in_base(int(message.text)):
            if not await ServiceDB.is_user_exist_by_barcode(int(message.text)):
                try:
                    await ServiceDB.add_user(message.from_user.id, int(message.text))
                    await state.set_state(UserRoadmap.main_menu)
                    await message.answer(
                        "Welcome to the club, buddy!",
                        reply_markup=go_to_main_menu(),
                    )
                except Exception as e:
                    print(f"Error during user registration: {e}")
                    await state.clear()
                    await message.answer("Произошла ошибка при регистрации. Попробуйте еще раз.")
            else:
                await message.answer("Этот barcode уже занят")
        elif len(message.text) == 6:
            await message.answer("Этого barcode нет в базе")
        else:
            await message.answer("Твой barcode неверен!")
    else:
        await message.answer("Barcode должен быть числом!")


# @user_router.message(UserRoadmap.main_menu, F.text == text_show_invite_code)
# async def user_show_invite_code(message: Message, state: FSMContext):
#     try:
#         invite_data = await ServiceDB.get_invite_info_by_tgid(message.from_user.id)
#         if invite_data and len(invite_data) == 2:
#             await message.answer(
#                 get_invite_message(invite_data[0], invite_data[1]),
#                 reply_markup=go_to_main_menu(),
#                 parse_mode="Markdown",
#             )
#         else:
#             await message.answer("Произошло что-то странное... Щелк* Ты ничего не видел.")
#     except Exception as e:
#         print(f"Error getting invite info: {e}")
#         await message.answer("Произошла ошибка при получении инвайт-кода.")


@user_router.message(UserRoadmap.main_menu, F.text == text_search_profiles)
async def user_search_profiles(message: Message, state: FSMContext):
    if await ServiceDB.is_profile_exist_by_tgid(message.from_user.id):
        await message.answer(
            text_search_profiles_start,
            reply_markup=welcome_keyboard(),
        )
        await state.set_state(SearchProfileStates.start)
    else:
        await message.answer(
            "Ты еще не создал свою анкету, создать?",
            reply_markup=yes_or_no_keyboard()
        )


@user_router.message(UserRoadmap.main_menu, F.text == text_yes)
async def user_create_profile(message: Message, state: FSMContext):
    await message.answer(
        text_profile_create_begin,
        reply_markup=understand_keyboard(),
    )
    await state.set_state(CreateProfileStates.start)


@user_router.message(UserRoadmap.main_menu, F.text == text_go_to_deepseek)
async def user_start_chat_with_ai(message: Message, state: FSMContext):
    llm_message = await llm_init_agent()
    await message.answer(
        llm_message,
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserRoadmap.llm_chat)


@user_router.message(UserRoadmap.llm_chat)
async def user_chat_with_ai(message: Message, state: FSMContext):
    if message.text:
        if message.text == '/cancel':
            await state.set_state(UserRoadmap.main_menu)
            await message.answer(
                "Уходишь? Ну ладно, приходи еще! 👋",
                reply_markup=main_menu_keyboard(),
            )
            return
        llm_message = await llm_generate_simple(message.text)
        await message.answer(
            llm_message,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Бот, Пожалуйста, введи текст для общения с ботом.",
            reply_markup=ReplyKeyboardRemove(),
        )


@user_router.message(UserRoadmap.main_menu, F.text == text_edit_profile)
async def user_start_edit_profile(message: Message, state: FSMContext):
    await message.answer(
        "Ну что же, давай отредактируем твою анкету",
        reply_markup=welcome_keyboard(),
    )
    await state.set_state(EditProfileStates.start)


@user_router.message(UserRoadmap.main_menu)
async def user_main_menu(message: Message, state: FSMContext):
    await message.answer(
        text_main_menu,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


@user_router.message()
async def user_message(message: Message, state: FSMContext):
    if await ServiceDB.is_user_exist_by_tgid(message.from_user.id):
        await message.answer(
            random.choice(text_main_menu_get_back),
            reply_markup=go_to_main_menu(),
        )
        await state.set_state(UserRoadmap.main_menu)
    else:
        await message.answer(
            "Сюда вход только по barcode, ну-ка документики пожалуйста 🕵🏿‍♂️",
            reply_markup=go_to_check_token(),
        )
        await state.set_state(UserRoadmap.get_token)
