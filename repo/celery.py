"""Celery file to set up celery in projects repo."""

import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "repo.settings")
app = Celery("repo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-for-comment-updates-every-30-minutes": {
        "task": "tasks.check_new_comments",
        "schedule": timedelta(minutes=30),
    }
}
