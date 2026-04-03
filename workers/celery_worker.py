import asyncio

from celery.signals import worker_process_init
from core.logger import logger
from database.minio_client import minio_client
from database.redis_client import redis_client
from workers.tasks import celery_app


@worker_process_init.connect
def init_worker_process(**kwargs):
    logger.info("Initializing connections in worker process...")
    
    try:
        minio_client.connect()
        logger.info("MinIO connected in worker process")
    except Exception as e:
        logger.error(f"Failed to connect MinIO: {e}")
        raise
    
    try:
        asyncio.run(redis_client.connect())
        logger.info("Redis connected in worker process")
    except Exception as e:
        logger.error(f"Failed to connect Redis: {e}")
        raise


app = celery_app
