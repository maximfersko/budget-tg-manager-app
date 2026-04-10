from celery.signals import worker_process_init

from core.logger import logger
from core.minio_client import minio_client
from workers.tasks.celery_config import celery_app


@worker_process_init.connect
def init_worker_process(**kwargs):
    logger.info("Initializing connections in worker process...")
    try:
        minio_client.connect()
        logger.info("MinIO connected in worker process")
    except Exception as e:
        logger.error(f"Failed to connect MinIO: {e}")
        raise


app = celery_app
