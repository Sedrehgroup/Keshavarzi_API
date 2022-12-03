from datetime import datetime, timedelta

from celery import shared_task

from config import celery_app
from regions.models import Region
from regions.utils import get_geojson_by_polygon


@shared_task()
def get_new_images():
    pass


def call_download_images_celery_task(instance: Region):
    end = datetime.now()
    start = end - timedelta(days=30)
    geom = get_geojson_by_polygon(instance.polygon)
    args = (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
            geom, instance.user_id, instance.id, instance.dates)
    task = celery_app.send_task("download_images", args)
    return task
