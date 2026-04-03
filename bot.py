import asyncio

from aiogram import Bot, Dispatcher

from core.config import BOT_TOKEN
from core.logger import logger
from database.engine import create_db
from database.redis_client import redis_client
from database.minio_client import minio_client
from tg_bot.handlers.commands import router as commands_router
from tg_bot.handlers.incomes import router as incomes_router
from tg_bot.handlers.statistics import router as statistics_router
from tg_bot.middlewares.db_middleware import DBMiddleware


async def main():
    await create_db()
    await redis_client.connect()
    minio_client.connect()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(DBMiddleware())
    dp.callback_query.middleware(DBMiddleware())

    dp.include_router(commands_router)
    dp.include_router(incomes_router)
    dp.include_router(statistics_router)

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Bot starting... ")

    try:
        await dp.start_polling(bot)
    finally:
        await redis_client.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
