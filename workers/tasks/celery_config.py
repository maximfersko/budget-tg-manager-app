from celery import Celery

from core.config import RABBITMQ_URL, REDIS_URL

celery_app = Celery('budget_bot')

celery_app.conf.update(
    broker_url=RABBITMQ_URL,
    result_backend=REDIS_URL,
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)

task_routes = {
    'workers.tasks.notifications.*': {'queue': 'high'},
    'workers.tasks.reports.*': {'queue': 'default'},
    'workers.tasks.analytics.*': {'queue': 'low'},
}
