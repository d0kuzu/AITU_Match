from asyncio import Lock

user_locks: dict[int, Lock] = {}

def get_lock(user_id: int) -> Lock:
    if user_id not in user_locks:
        user_locks[user_id] = Lock()
    return user_locks[user_id]