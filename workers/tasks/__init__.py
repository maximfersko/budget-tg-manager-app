from workers.tasks.celery_config import celery_app
from workers.tasks import notifications
from workers.tasks import process_file

celery = celery_app

__all__ = ['celery_app', 'celery']
