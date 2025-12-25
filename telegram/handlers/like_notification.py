import asyncio
import json
import logging

from aiogram import Router, F
from aiogram.enums import ParseMode, ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from config.enums import ActionStatusEnum
from database.repo import Repos
from services.helpers.send_photos import send_photos
from telegram.filters.registration import RegisteredFilter
from telegram.handlers.menu import show_menu
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import SeeLikeNotificationsStates, MenuStates
from telegram.misc.texts import TEXTS

router = Router()


@router.message(SeeLikeNotificationsStates.pending, F.text==TEXTS.notification_texts.see_likes)
async def see_likes(message: Message, state: FSMContext, repos: Repos):
    await message.answer(TEXTS.notification_texts.start_show, reply_markup=ReplyKeyboards.view_who_liked_actions())
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    notifications = await repos.notification.get_available()
    for notification in notifications:
        if notification.action.target_id == message.from_user.id:
            owner_id = notification.action.user_id
            owner_profile = await repos.profile.search_by_user_id(owner_id)

            if owner_profile is None:
                logging.info(f"skip notification for {owner_id} cause None profile")

            text = f"Твоя анкета понравилась: \n\n{owner_profile.name}, {owner_profile.age}, {owner_profile.uni.value} - {owner_profile.description}"
            if notification.action.message is not None:
                text += f'\n"{notification.action.message}"'

            await state.set_state(SeeLikeNotificationsStates.viewing_profile)
            await state.update_data(action_id=notification.action_id)
            await state.update_data(viewing_profile_id=owner_id, viewing_profile_name=owner_profile.name)

            await send_photos(message.bot, json.loads(owner_profile.s3_path), text, message.from_user.id)

            await repos.notification.delete_notification(notification.id)

    await message.answer(TEXTS.notification_texts.end_show)
    await asyncio.sleep(0.5)
    await state.set_state(MenuStates.main_menu)
    await show_menu(message)


@router.message(SeeLikeNotificationsStates.viewing_profile, F.text.in_([TEXTS.search_profiles_texts.like, TEXTS.search_profiles_texts.skip]))
async def viewing_profile(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()
    action_id = data.get("action_id")

    answer_type = ActionStatusEnum.ACCEPTED if message.text == TEXTS.search_profiles_texts.like else ActionStatusEnum.PENDING

    await repos.action.change_action_status(action_id, answer_type)

    if answer_type == ActionStatusEnum.ACCEPTED:
        owner_id = data.get("viewing_profile_id")
        owner_name = data.get("viewing_profile_name")

        userlink = f'<a href="tg://user?id={owner_id}">{owner_name}</a>'
        text = f"Отлично! Поспеши написать в чат первым. \n\nДержи ссылку на чат - {userlink}"

        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())

        #______TO OWNER______
        profile = await repos.profile.search_by_user_id(message.from_user.id)
        if profile is None:
            logging.error(f"sending mutual like to owner({owner_id}) error: target profile({message.from_user.id}) not found")
            return

        userlink = f'<a href="tg://user?id={message.from_user.id}">{profile.name}</a>'
        text = f"У тебя взаимный лайк!\n{profile.name}, {profile.age}, {profile.uni.value} - {profile.description} \n\nДержи ссылку на чат - {userlink}."
        await send_photos(message.bot, json.loads(profile.s3_path), text, owner_id)
