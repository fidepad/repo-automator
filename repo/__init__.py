from __future__ import absolute_import, unicode_literals

# This will make sure the app is imported when django starts so shared tasks would use it
from .celery import app as celery_app

__all__ = ('celery_app', )
