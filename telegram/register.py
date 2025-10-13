from aiogram import Dispatcher, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import repo
from database.session import get_db
from telegram.handlers import registration, admin
from telegram.middlewares.repo_middleware import RepoMiddleware
from telegram.middlewares.scheduler_middleware import SchedulerMiddleware

class TgRegister:
    def __init__(self, dp: Dispatcher, scheduler: AsyncIOScheduler, bot: Bot):
        self.user_repo = None

        self.dp = dp
        self.scheduler = scheduler
        self.bot = bot

        self.bot.user_repo = None

    async def register(self):
        await self._create_repos()
        self._register_handlers()
        self._register_middlewares()
        self._register_tasks()

    async def _create_repos(self):
        async with get_db() as session:
            self.user_repo = repo.UserRepo(session)

    def _register_handlers(self):
        self.dp.include_routers(registration.router)
        self.dp.include_routers(admin.router)

    def _register_middlewares(self):
        repo_middleware = RepoMiddleware(self.user_repo)
        scheduler_middleware = SchedulerMiddleware(self.scheduler)

        self.dp.callback_query.middleware(repo_middleware)
        self.dp.message.middleware(repo_middleware)
        self.dp.inline_query.middleware(repo_middleware)

        self.dp.callback_query.middleware(scheduler_middleware)
        self.dp.message.middleware(scheduler_middleware)
        self.dp.inline_query.middleware(scheduler_middleware)

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