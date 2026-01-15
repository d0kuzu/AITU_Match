import asyncio
import json

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.enums import ActionEnum, SexEnum, OppositeSexEnum, FlowEnum
from database.repo import Repos
from services.helpers.send_photos import send_photos
from telegram.handlers.menu import show_menu
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import MenuStates, SearchProfilesStates, ComplainStates
from telegram.misc.texts import TEXTS

router = Router()


@router.message(MenuStates.main_menu, F.text == TEXTS.menu_texts.search_profiles_text)
async def start_profiles_search(message: Message, state: FSMContext, repos: Repos):
    result = await repos.profile.get_sex_info(message.from_user.id)

    if result is None:
        await message.answer(TEXTS.error_texts.internal_error)
        return

    sex, opposite_sex = result

    await state.update_data(sex=sex.value, opposite_sex=opposite_sex.value)

    await message.answer(TEXTS.search_profiles_texts.start_search, reply_markup=ReplyKeyboards.profiles_search_actions())
    await state.update_data(flow=FlowEnum.EASY.value)
    await send_next_profile(message, state, repos)


async def send_next_profile(message: Message, state: FSMContext, repos: Repos, show_again=False):
    data = await state.get_data()

    if show_again:
        profile = repos.profile.search_by_user_id(data.get("current_viewing_tg_id"))
    else:
        profile = await repos.profile.search_random_user(message.from_user.id, SexEnum(data.get("sex")), OppositeSexEnum(data.get("opposite_sex")))

    if profile:
        await state.update_data(current_viewing_tg_id=profile.user_id)

        try:
            await send_photos(message.bot, json.loads(profile.s3_path),
                              (
                                  f"{profile.name}, {profile.age} лет, {profile.uni.value}\n"
                                  f"{profile.description}"
                              ), message.from_user.id)

            await state.set_state(SearchProfilesStates.viewing_profile)

        except FileNotFoundError:
            await message.answer(f"Ошибка: Файл фото не найден. Пробуем найти следующую анкету.")
            await send_next_profile(message, state, repos)
            return
        except Exception as e:
            await message.answer(f"Произошла ошибка при показе фото: {e}. Пробуем найти следующую анкету.")
            print(f"Error sending photo: {e}")
            await send_next_profile(message, state, repos)
            return
    else:
        await message.answer(
            "Других профилей не найдено 😭",
        )
        await state.set_state(MenuStates.main_menu)
        await show_menu(message, state)


@router.message(SearchProfilesStates.viewing_profile, F.text.in_([TEXTS.search_profiles_texts.like, TEXTS.search_profiles_texts.message, TEXTS.search_profiles_texts.skip, TEXTS.search_profiles_texts.leave, TEXTS.search_profiles_texts.complain]))
async def leave_profile_search(message: Message, state: FSMContext, repos: Repos):
    if message.text == TEXTS.search_profiles_texts.leave:
        await state.set_state(MenuStates.main_menu)
        await show_menu(message, state)
        return

    data = await state.get_data()

    target_id = data.get("current_viewing_tg_id")
    action = ActionEnum.like if message.text == TEXTS.search_profiles_texts.like \
        else ActionEnum.skip if message.text == TEXTS.search_profiles_texts.skip \
        else ActionEnum.message if message.text == TEXTS.search_profiles_texts.message else ActionEnum.complain

    if action == ActionEnum.like:
        action_id = await repos.action.create_action(message.from_user.id, target_id, ActionEnum.like)
        await repos.notification.create_notification(action_id)

        await send_next_profile(message, state, repos)
        return

    elif action == ActionEnum.skip:
        await repos.action.create_action(message.from_user.id, target_id, ActionEnum.skip)

        await send_next_profile(message, state, repos)
        return

    elif action == ActionEnum.message:
        await message.answer(TEXTS.search_profiles_texts.message_text)
        await state.set_state(SearchProfilesStates.wait_message)
        return

    else:
        await message.answer(TEXTS.complain_texts.ask_reason, reply_markup=ReplyKeyboards.complain_reasons())
        await state.set_state(ComplainStates.wait_reason)


@router.message(SearchProfilesStates.wait_message)
async def send_message(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()

    target_id = data.get("current_viewing_tg_id")

    action_id = await repos.action.create_action(message.from_user.id, target_id, ActionEnum.message, message.text)
    await repos.notification.create_notification(action_id)

    await send_next_profile(message, state, repos)


@router.message(ComplainStates.wait_reason, F.text.in_([TEXTS.complain_texts.mature_content, TEXTS.complain_texts.sell_add, TEXTS.complain_texts.do_not_like, TEXTS.complain_texts.other]))
async def wait_complain_reason(message: Message, state: FSMContext):
    await message.answer(TEXTS.complain_texts.add_comment, reply_markup=ReplyKeyboards.go_back())
    await state.set_state(ComplainStates.wait_comment)
    await state.update_data(reason=message.text)


@router.message(ComplainStates.wait_reason, F.text == TEXTS.complain_texts.back)
async def back_to_liking(message: Message, state: FSMContext, repos: Repos):
    await send_next_profile(message, state, repos, True)


@router.message(ComplainStates.wait_comment, F.text == TEXTS.complain_texts.back)
async def back_to_reasons(message: Message, state: FSMContext):
    await wait_complain_reason(message, state)


@router.message(ComplainStates.wait_comment)
async def send_complaint(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()
    reason = data.get("reason")
    target_id = data.get("current_viewing_tg_id")
    comment = message.text

    await repos.complaint.create(target_id, reason, comment)
    await repos.action.create_action(message.from_user.id, target_id, ActionEnum.complain)

    await message.answer(TEXTS.complain_texts.complain_sent, reply_markup=ReplyKeyboards.profiles_search_actions())

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    await send_next_profile(message, state, repos)
