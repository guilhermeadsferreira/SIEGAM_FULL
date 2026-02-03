from celery.schedules import crontab
import celery

from settings import settings

timezone = "America/Sao_Paulo"
enable_utc = False

beat_schedule = {
    "etl-daily-run": {
        "task": "main.download_file",
        "schedule": crontab(minute=0, hour=6),
    },
}

worker_prefetch_multiplier = 1
task_acks_late = True
task_reject_on_worker_lost = True

task_routes = {
    "main.*": {"queue": "etl"},
}

task_queues = {
    "etl": {
        "exchange": "etl",
        "routing_key": "etl",
    },
}

task_compression = "gzip"
task_serializer = "json"
accept_content = ["json"]

app = celery.Celery("main", backend=settings.REDIS_URL, broker=settings.REDIS_URL)
app.conf.update(
    timezone=timezone,
    enable_utc=enable_utc,
    beat_schedule=beat_schedule,
    worker_prefetch_multiplier=worker_prefetch_multiplier,
    task_acks_late=task_acks_late,
    task_reject_on_worker_lost=task_reject_on_worker_lost,
    task_routes=task_routes,
    task_queues=task_queues,
    task_compression=task_compression,
    task_serializer=task_serializer,
    accept_content=accept_content,
    task_always_eager=False,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
)
