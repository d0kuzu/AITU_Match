import asyncio
import logging

import coloredlogs
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import env
from database.main import init_db, close_db
from telegram.register import TgRegister


async def start():

    async def on_startup():
        await init_db()

    async def on_shutdown():
        await close_db()


    bot = Bot(env.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage)

    await init_db()

    await bot.set_my_commands([
        BotCommand(command='start', description='Начать!')
    ])

    tg_register = TgRegister(dp, bot)
    await tg_register.register()

    await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    logging.basicConfig(level=env.logging_level)
    coloredlogs.install()
    asyncio.run(start())
