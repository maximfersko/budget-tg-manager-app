from workers.tasks import notifications
from workers.tasks.celery_config import celery_app

celery = celery_app

__all__ = ['celery_app', 'celery']
