from __future__ import absolute_import,unicode_literals
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery("core")
app.config_from_object("django.conf:settings",namespace="CELERY")
app.autodiscover_tasks()
# app.conf.broker_connection_retry_on_startapp = True
app.autodiscover_tasks()