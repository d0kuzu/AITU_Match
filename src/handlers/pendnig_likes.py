import json
from typing import List, Optional

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, FSInputFile, ReplyKeyboardRemove

from src.handlers.likes import get_telegram_username_or_name
from src.keyboards.inline import view_likes_menu_keyboard
from src.keyboards.reply import main_menu_keyboard, pending_like_action_keyboard
from src.service.db_service import ServiceDB
from src.service.schemas import LikeSchema, ProfileSchema
from src.service.send_photo import send_photos
from src.states import ViewLikesStates

pending_router = Router()

@pending_router.callback_query(F.data == "view_who_liked_me")
async def process_view_who_liked_me(callback_query: CallbackQuery, state: FSMContext, bot: Bot):
    user_tg_id = callback_query.from_user.id

    pending_likes: List[LikeSchema] = await ServiceDB.get_pending_likes(liked_tgid=user_tg_id)

    if not pending_likes:
        await callback_query.message.answer("У тебя пока нет лайков.")
        await callback_query.answer(reply_markup=ReplyKeyboardRemove())
        return

    liker_ids = [like.liker_tgid for like in pending_likes]
    await state.update_data(pending_liker_ids=liker_ids, current_pending_index=0)
    await state.set_state(ViewLikesStates.viewing_pending_likes)

    await callback_query.message.delete()
    await callback_query.message.answer("Загружаю анкеты тех, кто вас лайкнул...", reply_markup=pending_like_action_keyboard())
    await show_next_pending_like_profile(callback_query.message, state, bot, callback_query.from_user.id)


async def show_next_pending_like_profile(target_message: Message, state: FSMContext, bot: Bot, user_id):
    user_tg_id = target_message.chat.id
    data = await state.get_data()
    pending_liker_ids: List[int] = data.get("pending_liker_ids", [])
    current_index: int = data.get("current_pending_index", 0)

    if not pending_liker_ids or current_index >= len(pending_liker_ids):
        await target_message.answer("Вы просмотрели все анкеты, которые вас лайкнули на данный момент.", reply_markup=main_menu_keyboard())
        await state.clear()
        return

    liker_tg_id_to_show = pending_liker_ids[current_index]

    profile_data: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(liker_tg_id_to_show)

    if profile_data:
        try:
            await send_photos(target_message, json.loads(profile_data.s3_path), (
                    f"Вам симпатизирует: {profile_data.name}, {profile_data.age} лет, {profile_data.uni}\n"
                    f"{profile_data.description}\n\n"
                ), user_id)

            await state.update_data(currently_viewed_pending_liker_id=liker_tg_id_to_show)
        except FileNotFoundError:
            await target_message.answer(f"Не удалось загрузить фото для профиля {profile_data.name}. Пропускаем...")
            await state.update_data(current_pending_index=current_index + 1)
            await show_next_pending_like_profile(target_message, state, bot, user_id)
        except Exception as e:
            await target_message.answer(f"Произошла ошибка при показе профиля: {e}. Пропускаем...")
            print(f"Error sending pending like profile: {e}")
            await state.update_data(current_pending_index=current_index + 1)
            await show_next_pending_like_profile(target_message, state, bot, user_id)
    else:
        await target_message.answer \
            (f"Не удалось найти профиль для пользователя с ID {liker_tg_id_to_show}. Пропускаем...")
        await state.update_data(current_pending_index=current_index + 1)
        await show_next_pending_like_profile(target_message, state, bot, user_id)


@pending_router.message(ViewLikesStates.viewing_pending_likes, F.text == "Лайкнуть в ответ ❤️")
async def process_accept_pending_like(message: Message, state: FSMContext, bot: Bot):
    liker_tg_id_str = await state.get_value("currently_viewed_pending_liker_id")
    liker_tg_id = int(liker_tg_id_str)
    current_user_tg_id = message.from_user.id

    await message.delete()

    await ServiceDB.accept_like(liker_tg_id, current_user_tg_id)
    await show_mutual_like_for_liker(liker_tg_id, message)
    await show_mutual_like_for_answerer(liker_tg_id, message)

    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(message, state, bot, message.from_user.id)


async def show_mutual_like_for_liker(liker_tg_id: str | int, message: Message):
    try:
        profile_data: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(message.from_user.id)
        telegram_user_info = await get_telegram_username_or_name(message.bot, message.from_user.id)

        await send_photos(message, json.loads(profile_data.s3_path), (
                f"Взаимная симпатия с: {profile_data.name}, {profile_data.age}\n"
                f"Университет: {profile_data.uni}\n"
                f"О себе: {profile_data.description}\n\n"
                f"Связь: {telegram_user_info}"
            ), liker_tg_id)
    except FileNotFoundError:
        await message.answer(
            f"Не удалось загрузить фото для профиля {message.from_user.username}")
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при показе профиля {message.from_user.username} Ошибка: {e}")
        print(f"Error sending mutual like profile: {e}")


async def show_mutual_like_for_answerer(liker_tg_id: str | int, message: Message):
    try:
        mutual_profile_tg_id = liker_tg_id
        profile_data: Optional[ProfileSchema] = await ServiceDB.get_profile_by_tgid(mutual_profile_tg_id)
        telegram_user_info = await get_telegram_username_or_name(message.bot, mutual_profile_tg_id)

        await send_photos(message, json.loads(profile_data.s3_path), (
                f"Вы ответили взаимностью - {profile_data.name}, {profile_data.age}\n"
                f"Университет: {profile_data.uni}\n"
                f"О себе: {profile_data.description}\n\n"
                f"Связь: {telegram_user_info}"
            ), )
    except FileNotFoundError:
        await message.answer(
            f"Не удалось загрузить фото для профиля {message.from_user.username}")
    except Exception as e:
        await message.answer(
            f"Произошла ошибка при показе профиля {message.from_user.username} Ошибка: {e}")
        print(f"Error sending mutual like profile: {e}")


@pending_router.message(ViewLikesStates.viewing_pending_likes, F.text == "Отклонить 👎")
async def process_reject_pending_like(message: Message, state: FSMContext, bot: Bot):
    liker_tg_id_str = await state.get_value("currently_viewed_pending_liker_id")
    liker_tg_id = int(liker_tg_id_str)
    current_user_tg_id = message.from_user.id

    await ServiceDB.reject_like(liker_tg_id, current_user_tg_id)

    try:
        await message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(message, state, bot, message.from_user.id)


@pending_router.message(ViewLikesStates.viewing_pending_likes, F.text == "➡️ Следующий")
async def process_next_pending_like_button(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_index = data.get("current_pending_index", 0)
    await state.update_data(current_pending_index=current_index + 1)
    await show_next_pending_like_profile(message, state, bot, message.from_user.id)