import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config')
celery_app.autodiscover_tasks(['regions.tasks'])

celery_app.conf.broker_url = f"amqp://{os.environ['RABBITMQ_USER']}:{os.environ['RABBITMQ_PASS']}@{os.environ['SERVER_IP']}"
celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.CELERY_BEAT_SCHEDULER = 'django-celery-beat.schedulers.DatabaseScheduler'

