import asyncio
from core.logger import logger
from services.ai_service import AIService
from services.vector_service import VectorService
from workers.tasks.celery_config import celery_app

@celery_app.task(name="tasks.ai.process_insight")
def process_ai_insight_task(user_id: int, summary_text: str, metadata: dict = None):
    async def _async_task():
        ai_service = AIService()
        vector_service = VectorService()

        logger.info(f"Task: Analyzing report for user {user_id}...")
        insight = await ai_service.extract_insight(summary_text)

        if not insight or not isinstance(insight, str):
            logger.warning(f"Task: No valid insight extracted for user {user_id}. Skipping.")
            return

        logger.info(f"Task: Saving insight to Qdrant for user {user_id}")
        await vector_service.save_insight(user_id, insight, metadata=metadata)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_async_task())
