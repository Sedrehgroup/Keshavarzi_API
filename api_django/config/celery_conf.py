import os
from datetime import timedelta

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('config')
celery_app.autodiscover_tasks(['regions.tasks'])

rabbit_user = os.environ['RABBITMQ_USER']
rabbit_pass = os.environ['RABBITMQ_PASS']
rabbit_port = os.environ['RABBITMQ_PORT']
server_ip = os.environ['SERVER_IP']

celery_app.conf.broker_url = f"amqp://{rabbit_user}:{rabbit_pass}@{server_ip}:{rabbit_port}"
celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 1
