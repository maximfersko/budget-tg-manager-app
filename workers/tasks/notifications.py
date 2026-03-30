import asyncio

from core.logger import logger
from workers.tasks.celery_config import celery_app


@celery_app.task(name="send_notifications", bind=True, max_retries=3)
def task_test(self, tg_id: int) -> dict:
    async def _send_notifications():
        logger.info(f"Sending notification task {tg_id}")

        return {"status": "ok", 'user_id': tg_id}

    try:
        asyncio.run(_send_notifications())
    except Exception as e:
        logger.error(e)
        raise self.retry(exc=e, countdown=60)
