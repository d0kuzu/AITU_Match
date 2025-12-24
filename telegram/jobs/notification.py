import json
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import StorageKey
from config.enums import FlowEnum, NotificationStateEnum
from database.repo import Repos
from database.session import get_db
from services.helpers.send_photos import send_photos


async def notification_sender(bot: Bot, dp: Dispatcher):
    async with get_db() as session:
        repos = Repos(session)

        notifications = await repos.notification.get_available()

        for notification in notifications:
            if notification.state != NotificationStateEnum.WAITING:
                continue

            target_id = notification.action.target_id
            owner_id = notification.action.user_id

            key = StorageKey(bot.id, target_id, target_id)
            target_data = await dp.storage.get_data(key)

            last_activity = target_data.get("last_activity", datetime.now())
            flow = target_data.get("flow", FlowEnum.EASY)

            if flow==FlowEnum.HARD and datetime.now() - last_activity < timedelta(minutes=5):
                continue

            owner_profile = repos.profile.search_by_user_id(owner_id)
            if owner_profile is None:
                logging.info(f"skip notification for {owner_id} cause None profile")

            # text = f"Твоя анкета понравилась: \n\n{owner_profile.name}, {owner_profile.age}, {owner_profile.uni.value} - {owner_profile.description}"
            #
            # await send_photos(bot, json.loads(owner_profile.s3_path), text, target_id)

            # repos.notification.delete_notification(notification.id)
            repos.notification.set_sent_state(notification.id)  #TODO: add ваша анкета понравилась /кол-во лайков/
