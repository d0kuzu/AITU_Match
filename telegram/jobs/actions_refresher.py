from datetime import datetime, timedelta

from database.repo import Repos
from database.session import get_db


async def actions_refresher():
    async with get_db() as session:
        repos = Repos(session)

        actions = await repos.action.get_all_actions()
        for action in actions:
            if action.created_at <= datetime.now() - timedelta(days=10):
                await repos.action.delete_action(action.id)
