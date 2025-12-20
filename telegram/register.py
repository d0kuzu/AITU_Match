from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config.config import Environ
from database import repo
from database.session import get_db
from telegram.handlers import registration, admin, search_profiles
from telegram.middlewares.env_middleware import EnvMiddleware
from telegram.middlewares.repo_middleware import RepoMiddleware
from telegram.middlewares.scheduler_middleware import SchedulerMiddleware

class TgRegister:
    def __init__(self, dp: Dispatcher, bot: Bot):

        self.dp = dp
        self.bot = bot

        self.scheduler = None
        self.env = None

    async def register(self):
        self._create_scheduler()
        self._create_env()

        self._register_handlers()
        self._register_middlewares()
        self._register_tasks()

    def _create_scheduler(self):
        scheduler = AsyncIOScheduler(timezone=None)
        scheduler.start()
        self.scheduler = scheduler

    def _create_env(self):
        env = Environ()
        self.env = env

    def _register_handlers(self):
        self.dp.include_routers(admin.router)
        self.dp.include_routers(registration.router)
        self.dp.include_routers(search_profiles.router)

    def _register_middlewares(self):
        repo_middleware = RepoMiddleware()
        scheduler_middleware = SchedulerMiddleware(self.scheduler)
        env_middleware = EnvMiddleware(self.env)

        self.dp.callback_query.middleware(repo_middleware)
        self.dp.message.middleware(repo_middleware)
        self.dp.inline_query.middleware(repo_middleware)

        self.dp.callback_query.middleware(scheduler_middleware)
        self.dp.message.middleware(scheduler_middleware)
        self.dp.inline_query.middleware(scheduler_middleware)

        self.dp.callback_query.middleware(env_middleware)
        self.dp.message.middleware(env_middleware)
        self.dp.inline_query.middleware(env_middleware)

    def _register_tasks(self):
        ### OLD STRUCTURE ###
        # self.scheduler.add_job(
        #     func=counter_task,
        #     trigger=morning_trigger,
        #     args=[self.bot, self.user_repo],
        # )
        # self.scheduler.add_job(
        #     func=bot_message_task,
        #     trigger=afternoon_trigger,
        #     args=[self.bot, self.dp.storage, self.user_repo, AFFIRMATION_TASK_PROMPT],
        # )
        # self.scheduler.add_job(
        #     func=bot_message_task,
        #     trigger=evening_trigger,
        #     args=[self.bot, self.dp.storage, self.user_repo, QUESTION_TASK_PROMPT],
        # )
        # self.scheduler.add_job(
        #     func=bot_message_task,
        #     trigger=twilight_trigger,
        #     args=[self.bot, self.dp.storage, self.user_repo, AFFIRMATION_TASK_PROMPT],
        # )
        # self.scheduler.add_job(
        #     func=ask_if_held_out,
        #     trigger=ask_trigger,
        #     args=[self.bot, self.user_repo],
        # )
        pass