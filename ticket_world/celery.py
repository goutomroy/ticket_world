from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ticket_world.settings")


class Config:
    broker_url = "redis://localhost:6379/0"
    result_backend = "django-db"
    beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
    beat_max_loop_interval = 600
    result_cache_max = 1000
    soft_time_limit = 5
    # worker_concurrency = 4
    task_compression = "gzip"
    result_compression = "gzip"
    result_persistent = True
    task_track_started = True
    task_publish_retry = True
    task_publish_retry_policy = {
        "max_retries": 3,
        "interval_start": 0.2,
        "interval_step": 0.2,
        "interval_max": 1,
    }


app = Celery("ticket_world")
app.config_from_object(Config(), namespace="CELERY")
app.autodiscover_tasks()
