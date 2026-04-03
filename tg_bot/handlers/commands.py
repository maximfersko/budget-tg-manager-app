from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.logger import logger

router = Router(name="user_commands_router")


@router.message(CommandStart())
async def cmd_start_handler(message: Message):
    username = message.from_user.first_name

    logger.info(f"User {message.from_user.id} ({username}) typed /start")

    await message.answer(
        text=f"Hello, {username}! 👋\n\n"
             f"I am your personal Telegram finance manager.\n"
             f"Send me an amount or choose an action below."
    )
