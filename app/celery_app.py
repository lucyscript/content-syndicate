"""
Celery configuration for ContentSyndicate
"""
import os
from celery import Celery
from .config import settings

# Create Celery instance
celery_app = Celery(
    "contentsyndicate",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    beat_schedule={
        "sync-rss-feeds": {
            "task": "app.tasks.sync_rss_feeds",
            "schedule": 3600.0,  # Every hour
        },
        "process-content-queue": {
            "task": "app.tasks.process_content_queue",
            "schedule": 300.0,  # Every 5 minutes
        },
        "send-scheduled-newsletters": {
            "task": "app.tasks.send_scheduled_newsletters",
            "schedule": 600.0,  # Every 10 minutes
        },
        "cleanup-analytics": {
            "task": "app.tasks.cleanup_old_analytics",
            "schedule": 86400.0,  # Daily
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
