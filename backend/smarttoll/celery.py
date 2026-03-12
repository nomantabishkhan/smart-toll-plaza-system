import os
import warnings
from celery import Celery

# Suppress requests/chardet version mismatch (chardet 7.x from reportlab
# triggers a stale check_compatibility assertion in requests).
warnings.filterwarnings("ignore", message="urllib3.*chardet.*charset_normalizer")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarttoll.settings")

app = Celery("smarttoll")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
