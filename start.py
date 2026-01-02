import asyncio
import logging

import coloredlogs
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from redis import Redis

from config.config import Environ
from database.main import init_db, close_db
from telegram.register import TgRegister


async def start(environ: Environ):

    async def on_startup():
        await init_db(environ.db.asyncpg_url)

    async def on_shutdown():
        await close_db()


    bot = Bot(environ.bot.token)
    redis = Redis(host=environ.redis.host, port=environ.redis.port, db=environ.redis.db)
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)
    await init_db(environ.db.asyncpg_url)

    await bot.set_my_commands([
        BotCommand(command='menu', description='В меню'),
        BotCommand(command='my_profile', description='Мой профиль')
    ])

    tg_register = TgRegister(dp, bot, environ)
    await tg_register.register()

    await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    env = Environ()

    logging.basicConfig(level=env.bot.logging_level)
    coloredlogs.install()
    asyncio.run(start(env))
