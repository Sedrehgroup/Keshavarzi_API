import os
from datetime import timedelta

from celery import Celery

celery_app = Celery('config')