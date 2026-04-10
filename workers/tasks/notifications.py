import asyncio

from aiogram import Bot

from core.config import BOT_TOKEN
from core.logger import logger
from workers.tasks.celery_config import celery_app


@celery_app.task(bind=True, max_retries=3)
def notify_user_file_processed(self, user_id: int, result: dict) -> dict:

    async def _send_notification():
        bot = Bot(token=BOT_TOKEN)
        
        try:
            if result.get("status") == "success":
                message = (
                    f"File processed successfully!\n\n"
                    f"Added operations: {result['added']}\n"
                    f"Duplicates skipped: {result['duplicates']}\n"
                    f"Stored in: {result['s3_key']}"
                )
            else:
                message = (
                    f"File processing failed\n\n"
                    f"Error: {result.get('error', 'Unknown error')}"
                )
            
            await bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Notification sent to user {user_id}")
            
            await bot.session.close()
            return {"status": "sent", "user_id": user_id}
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            await bot.session.close()
            raise
    
    try:
        result = asyncio.run(_send_notification())
        return result
    
    except Exception as e:
        retry_num = self.request.retries + 1
        logger.error(f"Notification task failed, retry {retry_num}/{self.max_retries}: {e}")
        
        if self.request.retries >= self.max_retries:
            logger.error("Max retries reached for notification")
            return {"status": "failed", "error": str(e)}
        
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=e, countdown=countdown)
