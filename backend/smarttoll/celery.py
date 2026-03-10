import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarttoll.settings")

app = Celery("smarttoll")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Windows-friendly worker defaults
app.conf.worker_pool = "solo"
app.conf.worker_concurrency = 1

app.autodiscover_tasks()
