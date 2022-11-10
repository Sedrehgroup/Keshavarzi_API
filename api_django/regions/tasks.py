import logging
from datetime import timedelta, datetime
from time import sleep

import requests
import ee
import os

from celery import shared_task
from celery.result import AsyncResult
from django.conf import settings
from django.utils.timezone import now
from geoserver.catalog import ConflictingDataError

from regions.models import Region
from regions.utils import get_geojson_by_polygon
from utils.gee.utils import get_and_validate_date_range, get_and_validate_polygon_by_geom, get_dates_of_image_collection, get_image_collections
from utils.geoserver.base import cat

logger = logging.getLogger(__name__)


@shared_task()
def download_images(start, end, polygon_geojson, user_id, region_id, dates):
    region = Region.objects.get(id=region_id)
    start, end = get_and_validate_date_range(start, end)
    polygon = get_and_validate_polygon_by_geom(polygon_geojson)
    folder_path = region.folder_path
    os.makedirs(folder_path, exist_ok=True)
    dates = dates if dates is not None else ""

    image_collection = get_image_collections(polygon, start, end)
    id_date_list = get_dates_of_image_collection(image_collection)

    logger.info("Start downloading images")
    for img_id, img_date in id_date_list:
        url = ee.Image(img_id).getDownloadURL(params={
            'scale': 10, 'region': polygon, "bands": ['TCI_R', 'TCI_G', 'TCI_B'],
            'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

        # Example: /media/images/user-1/region-1/2022-01-02.tif
        file_path = region.get_file_path_by_date_and_folder_path(img_date, folder_path)
        dates += f"{img_date}\n"
        with requests.get(url) as response:
            # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
            with open(file_path, 'wb') as raster_file:
                raster_file.write(response.content)

        try:
            cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}--{img_date}", data=file_path)
        except ConflictingDataError as e:
            logger.error(e)

    region.dates = dates
    region.date_last_download = now()
    region.save(update_fields=["dates", "date_last_download"])


@shared_task()
def get_new_images():
    """
        Step 1: Get target regions( region.date_last_download is older that 7 days ago )
        Step 2: Slice regions to smaller and nested list: [1,2,3,4,5,6,7] -> [[1,2,3], [4,5,6], [7]]
        Step 3: Download every small region list images and wait for !PENDING stats
        STEP 4: Check that tasks are done without FAILURE stats
        STEP 5: Check that tasks are done with SUCCESS stats
        STEP 6: Update region.date_last_update field of small region list.
        ** DONE **
    """
    date_today = datetime.today()
    date_weak_ago = date_today - timedelta(days=7)
    regions = Region.objects \
        .filter(date_last_download__lt=date_weak_ago) \
        .only("id", "user_id", "polygon")
    mdipt = getattr(settings, "MAXIMUM_DOWNLOAD_IMAGE_PER_TASK", 3)
    sliced_regions = [regions[i:i + mdipt] for i in range(0, len(regions), mdipt)]

    def get_tasks(region_list: list):
        result = []
        for region in region_list:
            task = download_images.delay(start=date_weak_ago, end=date_today,
                                         polygon_geojson=get_geojson_by_polygon(region.polygon),
                                         user_id=region.user_id, region_id=region.id, dates=region.dates)
            result.append(task)
        return result

    for region_slice in sliced_regions:
        tasks_list = get_tasks(region_slice)
        while all(AsyncResult(task.id).state != "PENDING" for task in tasks_list):
            sleep(1)

        if not all(AsyncResult(task.id).state != "FAILURE" for task in tasks_list):
            for task in tasks_list:
                async_result = AsyncResult(task.id)
                if async_result.state == "FAILURE":
                    logger.error(f"Task with ID={task.id} is failed. Result={async_result.result}")
                    break
        elif not all(AsyncResult(task.id).state != "SUCCESS" for task in tasks_list):
            for task in tasks_list:
                async_result = AsyncResult(task.id)
                if async_result.state == "SUCCESS":
                    logger.error(f"Task with ID={task.id} is not success. Result={async_result.result}")
                    break

        bulk_list = []
        for region in region_slice:
            region.date_last_download = date_today
            bulk_list.append(region)
        Region.objects.bulk_update(bulk_list, ["date_last_download"])
