from celery import Celery
from celery.utils.log import get_task_logger

from .settings import get_settings

celery = Celery(
    __name__,
    broker=get_settings().CELERY_BROKER_URI,
    backend=get_settings().CELERY_BACKEND_URI,
)

celery_log = get_task_logger(__name__)

celery.autodiscover_tasks()
