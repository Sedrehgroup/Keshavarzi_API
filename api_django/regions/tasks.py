import logging
from datetime import datetime, timedelta

from celery import shared_task

from config import celery_app
from regions.models import Region
from regions.utils import get_geojson_by_polygon

logger = logging.getLogger("celery_tasks")

@shared_task()
def get_new_images():
    pass


