from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.enums import SexEnum
from database.repo import Repos
from telegram.filters.registration import RegisteredFilter
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(RegisteredFilter())


async def find_next_profile(user_id: int, opposite_sex: SexEnum)


async def send_next_profile(target_message: Message, state: FSMContext, repos: Repos):
    profile = await repos.profile.search_profile(target_message.from_user.id)
    await find_next_profile(profile.user_id, profile.opposite_sex)

    if profile:
        await state.update_data(current_viewing_tg_id=profile.tg_id)

        try:
            await send_photos(target_message, json.loads(profile.s3_path),
                              (
                                  f"{profile.name}, {profile.age} лет, {profile.uni}\n"
                                  f"{profile.description}"
                              ))

            await state.set_state(SearchProfileStates.viewing_profile)

        except FileNotFoundError:
            await target_message.answer(f"Ошибка: Файл фото не найден. Пробуем найти следующую анкету.")
            await send_next_profile(target_message, curr_user_tgid, state, bot)
        except Exception as e:
            await target_message.answer(f"Произошла ошибка при показе фото: {e}. Пробуем найти следующую анкету.")
            print(f"Error sending photo: {e}")
            await send_next_profile(target_message, curr_user_tgid, state, bot)


    else:
        await target_message.answer(
            "Других профилей не найдено 😭",
            reply_markup=main_menu_keyboard()
        )
        await state.set_state(UserRoadmap.main_menu)


@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.search_profiles_text)
async def start_profiles_search(message: Message, state: FSMContext, repos: Repos):
    await state.clear()
    await message.answer("Начинаем поиск анкет...", reply_markup=ReplyKeyboards.profiles_search_actions())
    await send_next_profile(message, state, repos)
