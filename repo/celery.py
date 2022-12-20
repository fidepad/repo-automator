"""Celery file to set up celery in projects repo"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'repo.settings')
app = Celery('repo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
