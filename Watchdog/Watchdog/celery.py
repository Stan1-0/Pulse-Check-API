import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Watchdog.settings')

app = Celery('Watchdog')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()