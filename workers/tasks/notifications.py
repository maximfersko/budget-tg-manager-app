import asyncio

from core.logger import logger
from workers.tasks.celery_config import celery_app


@celery_app.task(bind=True, max_retries=3)
def task_test(self, tg_id: int) -> dict:
    
    async def _send_notifications():
        logger.info(f"Sending notification to user {tg_id}")
        

        return {"status": "ok", "user_id": tg_id}
    
    try:
        result = asyncio.run(_send_notifications())
        logger.info(f"Task completed successfully: {result}")
        return result
        
    except ValueError as e:

        logger.error(f"Validation error: {e}")
        return {"status": "failed", "error": str(e)}
        
    except Exception as e:

        retry_num = self.request.retries + 1
        logger.error(f"Task failed, retry {retry_num}/{self.max_retries}: {e}")
        
        if self.request.retries >= self.max_retries:
            logger.error("Max retries reached, giving up")
            return {"status": "failed", "error": str(e)}
        

        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
