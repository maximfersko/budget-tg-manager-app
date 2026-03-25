import asyncio
from aiogram import Bot, Dispatcher

from core.logger import logger
from core.config import BOT_TOKEN
from tg_bot.handlers.commands import router as commands_router
from tg_bot.handlers.incomes import router as incomes_router
from tg_bot.handlers.statistics import router as statistics_router

from tg_bot.middlewares.db_middleware import DBMiddleware
from database.engine import create_db

async def main():
    await create_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(DBMiddleware())
    dp.callback_query.middleware(DBMiddleware())

    dp.include_router(commands_router)
    dp.include_router(incomes_router)
    dp.include_router(statistics_router)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot starting... ")

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
