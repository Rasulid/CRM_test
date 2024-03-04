from celery import Celery
from core.config import settings

celery = Celery(
    "async_task",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    # backend=settings.SYNC_CELERY_DATABASE_URI,
    include=["app.api.v1.celery_tasks"],  # route where tasks are defined
)


# celery.config_from_object(settings, namespace='CELERY')
# celery.conf.update({"beat_dburi": settings.SYNC_CELERY_BEAT_DATABASE_URI})
celery.autodiscover_tasks()
