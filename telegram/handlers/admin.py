import asyncio
import logging

from aiogram import Router
from telegram.filters.role import AdminFilter

router = Router()
router.message.filter(AdminFilter())

