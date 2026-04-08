import asyncio
from workers.tasks.celery_config import celery_app
from services.ai_service import AIService
from services.vector_service import VectorService
from core.logger import logger

@celery_app.task(name="tasks.ai.process_insight")
def process_ai_insight_task(user_id: int, summary_text: str, metadata: dict):

    logger.info(f"Starting background AI insight extraction for user {user_id}")
    
    async def _async_task():
        ai_service = AIService()
        vector_service = VectorService()
        
        logger.info("Task: Extracting insight from summary...")
        insight = await ai_service.extract_insight(summary_text)
        
        logger.info(f"Task: Saving insight to Qdrant: {insight[:50]}...")
        await vector_service.save_insight(user_id, insight, metadata=metadata)
        
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_async_task())
    else:
        loop.run_until_complete(_async_task())
    
    logger.info(f"Background AI insight task completed for user {user_id}")
