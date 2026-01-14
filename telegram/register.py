from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import Environ
from database import repo
from database.session import get_db
from telegram.handlers import registration, search_profiles, like_notification, edit_profile, deactivate
from telegram.jobs.actions_refresher import actions_refresher
from telegram.jobs.notification import notification_sender
from telegram.middlewares.env_middleware import EnvMiddleware
from telegram.middlewares.last_activity_middleware import LastActivityMiddleware
from telegram.middlewares.repo_middleware import RepoMiddleware
from telegram.middlewares.scheduler_middleware import SchedulerMiddleware

class TgRegister:
    def __init__(self, dp: Dispatcher, bot: Bot, env: Environ):
        self.dp = dp
        self.bot = bot

        self.scheduler: AsyncIOScheduler|None = None
        self.env = env

    async def register(self):
        self._create_scheduler()

        self._register_handlers()
        self._register_middlewares()
        self._register_tasks()

    def _create_scheduler(self):
        scheduler = AsyncIOScheduler(timezone=None)
        scheduler.start()
        self.scheduler = scheduler

    def _register_handlers(self):
        self.dp.include_routers(registration.router)
        self.dp.include_routers(search_profiles.router)
        self.dp.include_routers(like_notification.router)
        self.dp.include_routers(edit_profile.router)
        self.dp.include_routers(deactivate.router)

    def _register_middlewares(self):
        repo_middleware = RepoMiddleware()
        scheduler_middleware = SchedulerMiddleware(self.scheduler)
        env_middleware = EnvMiddleware(self.env)
        last_activity_middleware = LastActivityMiddleware()

        self.dp.callback_query.middleware(last_activity_middleware)
        self.dp.callback_query.middleware(repo_middleware)
        self.dp.callback_query.middleware(scheduler_middleware)
        self.dp.callback_query.middleware(env_middleware)

        self.dp.message.middleware(last_activity_middleware)
        self.dp.message.middleware(repo_middleware)
        self.dp.message.middleware(scheduler_middleware)
        self.dp.message.middleware(env_middleware)

        self.dp.inline_query.middleware(last_activity_middleware)
        self.dp.inline_query.middleware(repo_middleware)
        self.dp.inline_query.middleware(scheduler_middleware)
        self.dp.inline_query.middleware(env_middleware)

    def _register_tasks(self):
        self.scheduler.add_job(
            func=notification_sender,
            trigger="interval",
            minutes=1,
            args=[self.bot, self.dp],
        )

        self.scheduler.add_job(
            func=actions_refresher,
            trigger="cron",
            hour=0,
            minute=0,
            args=[self.bot, self.dp],
        )
