from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from core.logger import logger
from database.repo import DBRepository

router = Router(name="user_commands_router")


@router.message(CommandStart())
async def cmd_start_handler(message: Message, repo: DBRepository):
    username = message.from_user.first_name

    logger.info(f"User {message.from_user.id} ({username}) typed /start")
    
    # Register user in database
    await repo.add_user(
        tg_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username
    )

    await message.answer(
        text=f"Hello, {username}!\n\n"
             f"I am your personal Telegram finance manager.\n"
             f"Send me an amount or choose an action below."
    )
