from workers.tasks.celery_config import celery_app

from workers.tasks import notifications

celery = celery_app

__all__ = ['celery_app', 'celery']
