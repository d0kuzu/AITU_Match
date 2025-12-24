import json
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ReplyKeyboardMarkup

from config.enums import FlowEnum, NotificationStateEnum
from database.repo import Repos
from database.session import get_db
from telegram.misc.keyboards import ReplyKeyboards
from telegram.misc.states import SeeLikeNotificationsStates
from telegram.misc.texts import TEXTS


async def notification_sender(bot: Bot, dp: Dispatcher):
    async with get_db() as session:
        repos = Repos(session)

        notifications = await repos.notification.get_available()

        should_notify_users = {}

        for notification in notifications:
            target_id = notification.action.target_id

            if notification.state == NotificationStateEnum.WAITING and should_notify_users.get(target_id) is None:
                should_notify_users[target_id] = 1

                key = StorageKey(bot.id, target_id, target_id)
                target_data = await dp.storage.get_data(key)

                last_activity = target_data.get("last_activity", datetime.now())
                flow = target_data.get("flow", FlowEnum.EASY)

                if flow == FlowEnum.HARD and datetime.now() - last_activity < timedelta(minutes=5):
                    continue

                await dp.storage.set_state(key, SeeLikeNotificationsStates.pending)

            elif should_notify_users.get(target_id) is not None:
                should_notify_users[target_id] += 1

            if notification.state == NotificationStateEnum.WAITING:
                await repos.notification.set_sent_state(notification.id)


        for target in should_notify_users:
            count = should_notify_users[target]
            text = TEXTS.notification_texts.notify_like \
                if count == 1 else TEXTS.notification_texts.notify_likes.format(count=count)
            await bot.send_message(target, text, reply_markup=ReplyKeyboards.view_who_liked())
