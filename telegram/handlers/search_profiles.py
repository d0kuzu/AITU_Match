import json

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.enums import SexEnum
from database.repo import Repos
from services.helpers.send_photos import send_photos
from telegram.filters.registration import RegisteredFilter
from telegram.handlers.menu import show_menu
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates, SearchProfilesStates
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(RegisteredFilter())


async def send_next_profile(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()
    profile = await repos.profile.search_random_user(message.from_user.id, data.get("sex"), data.get("opposite_sex"))

    if profile:
        await state.update_data(current_viewing_tg_id=profile.tg_id)

        try:
            await send_photos(message, json.loads(profile.s3_path),
                              (
                                  f"{profile.name}, {profile.age} лет, {profile.uni}\n"
                                  f"{profile.description}"
                              ))

            await state.set_state(SearchProfilesStates.viewing_profile) ##TODO

        except FileNotFoundError:
            await message.answer(f"Ошибка: Файл фото не найден. Пробуем найти следующую анкету.")
            await send_next_profile(message, state, repos)
        except Exception as e:
            await message.answer(f"Произошла ошибка при показе фото: {e}. Пробуем найти следующую анкету.")
            print(f"Error sending photo: {e}")
            await send_next_profile(message, state, repos)


    else:
        await message.answer(
            "Других профилей не найдено 😭",
        )
        await state.set_state(MenuStates.main_menu)
        await show_menu(message)


@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.search_profiles_text)
async def start_profiles_search(message: Message, state: FSMContext, repos: Repos):
    await state.clear()

    result = await repos.profile.get_sex_info(message.from_user.id)

    if result is None:
        await message.answer(TEXTS.error_texts.internal_error)
        return

    sex, opposite_sex = result
    await state.update_data(sex=sex, opposite_sex=opposite_sex)

    await message.answer("Начинаем поиск анкет...", reply_markup=ReplyKeyboards.profiles_search_actions())
    await send_next_profile(message, state, repos)
