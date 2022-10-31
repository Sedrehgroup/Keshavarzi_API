import os
from datetime import timedelta

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('FirstPrj')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['regions.tasks'])

app.conf.broker_url = 'amqp://rabbitmq'
app.conf.result_backend = 'rpc://'
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_expires = timedelta(days=1)
app.conf.task_always_eager = False
app.conf.worker_prefetch_multiplier = 1
app.conf.CELERY_BEAT_SCHEDULER = 'django-celery-beat.schedulers.DatabaseScheduler'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
