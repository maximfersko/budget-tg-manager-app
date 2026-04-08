import asyncio

from aiogram import Bot, Dispatcher

from core.config import BOT_TOKEN
from core.logger import logger
from core.minio_client import minio_client
from core.redis_client import redis_client
from database.engine import create_db
from tg_bot.handlers.admin import router as admin_router
from tg_bot.handlers.commands import router as commands_router
from tg_bot.handlers.incomes import router as incomes_router
from tg_bot.handlers.profile import router as profile_router
from tg_bot.handlers.statistics import router as statistics_router
from tg_bot.middlewares.db_middleware import DBMiddleware
from tg_bot.middlewares.role_middleware import RoleMiddleware


async def main():
    await create_db()
    await redis_client.connect()
    minio_client.connect()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(DBMiddleware())
    dp.callback_query.middleware(DBMiddleware())
    
    dp.message.middleware(RoleMiddleware())
    dp.callback_query.middleware(RoleMiddleware())

    dp.include_router(commands_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
    dp.include_router(incomes_router)
    dp.include_router(statistics_router)

    await bot.delete_webhook(drop_pending_updates=True)

    await init_first_admin()

    logger.info("Bot starting...")

    try:
        await dp.start_polling(bot)
    finally:
        await redis_client.close()


async def init_first_admin():
    from core.config import FIRST_ADMIN_ID
    from database.engine import async_session
    from database.models import UserRole
    from database.repo import DBRepository
    
    async with async_session() as session:
        repo = DBRepository(session)
        user = await repo.get_user_by_tg_id(FIRST_ADMIN_ID)
        
        if user and not user.is_admin():
            await repo.assign_role_to_user(FIRST_ADMIN_ID, UserRole.ADMIN.value)
            logger.info(f"Admin role assigned to {FIRST_ADMIN_ID}")
        elif user and user.is_admin():
            logger.info(f"User {FIRST_ADMIN_ID} is already admin")
        else:
            logger.info(f"Admin user {FIRST_ADMIN_ID} not found yet")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted")
