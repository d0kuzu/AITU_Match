import json
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.repo import Repos
from services.helpers.send_photos import send_photos
from telegram.filters.registration import RegisteredFilter
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import SeeLikeNotificationsStates
from telegram.misc.texts import TEXTS

router = Router()

router.message.filter(RegisteredFilter())

@router.message(SeeLikeNotificationsStates.pending, F.text==TEXTS.notification_texts.see_likes)
async def see_likes(message: Message, state: FSMContext, repos: Repos):
    notifications = await repos.notification.get_available()
    for notification in notifications:
        if notification.action.target_id == message.from_user.id:
            owner_id = notification.action.user_id
            owner_profile = repos.profile.search_by_user_id(owner_id)

            if owner_profile is None:
                logging.info(f"skip notification for {owner_id} cause None profile")

            text = f"Твоя анкета понравилась: \n\n{owner_profile.name}, {owner_profile.age}, {owner_profile.uni.value} - {owner_profile.description}"
            if notification.action.message is not None:
                text += f'\n"{notification.action.message}"'

            await state.set_state(SeeLikeNotificationsStates.viewing_profile)
            await state.update_data(action_id=notification.action_id)

            await message.edit_reply_markup(reply_markup=ReplyKeyboards.view_who_liked_actions())
            await send_photos(message.bot, json.loads(owner_profile.s3_path), text, message.from_user.id)

            repos.notification.delete_notification(notification.id)

@router.message(SeeLikeNotificationsStates.viewing_profile, F.text in [TEXTS.search_profiles_texts.like, TEXTS.search_profiles_texts.skip])
async def viewing_profile(message: Message, state: FSMContext, repos: Repos):
    data = await state.get_data()
    action_id = data.get("action_id")


