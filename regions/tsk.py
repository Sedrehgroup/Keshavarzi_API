import ee
import logging
import rasterio
import requests

from datetime import timedelta, datetime
from io import BytesIO
from time import sleep

from celery import shared_task
from celery.result import AsyncResult
from celery.exceptions import InvalidTaskError, TaskError
from django.conf import settings
from django.utils.timezone import now
from geoserver.catalog import ConflictingDataError

from config import celery_app
from regions.models import Region
from regions.utils import get_geojson_by_polygon
from utils.gee.utils import get_and_validate_date_range, get_and_validate_polygon_by_geom, \
    get_dates_of_image_collection, get_image_collections
from utils.geoserver.base import cat

logger = logging.getLogger(__name__)


@shared_task()
def download_images(start, end, polygon_geojson, user_id, region_id, dates):
    logger.debug("Start task -> download_images")
    try:
        region = Region.objects.get(id=region_id)
        start, end = get_and_validate_date_range(start, end)
        polygon = get_and_validate_polygon_by_geom(polygon_geojson)
    except Exception as e:
        logger.error(e)
        raise InvalidTaskError(e)

    image_collection = get_image_collections(polygon, start, end)
    id_date_list = get_dates_of_image_collection(image_collection)

    region.create_ndvi_rgb_dir()
    dates = dates if dates else ""
    last_image_date = ""
    logger.debug("Start downloading images")
    for img_id, img_date in id_date_list:
        last_image_date = img_date
        url = ee.Image(img_id).getDownloadURL(params={
            'scale': 10, 'region': polygon,
            "bands": ['TCI_R', 'TCI_G', 'TCI_B', 'B4', 'B8'],
            'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

        ndvi_file_path = region.get_ndvi_path(img_date)  # Example: /media/images/user-1/region-1/ndvi/2022-01-02.tif
        rgb_file_path = region.get_rgb_path(img_date)  # Example: /media/images/user-1/region-1/rgb/2022-01-02.tif
        dates += f"{img_date}\n"
        with requests.get(url) as response:
            with BytesIO(response.content) as content:
                with rasterio.open(content) as raster_file:
                    b4, b8 = raster_file.read(4), raster_file.read(5)  # ['TCI_R', 'TCI_G', 'TCI_B', 'B4', 'B8']
                    ndvi_result = (b8 - b4) / (b8 + b4)
                    rgb_result = raster_file.read((1, 2, 3))

                    meta = raster_file.meta
                    meta.update({"width": raster_file.width, "height": raster_file.height,
                                 "driver": 'GTiff', "dtype": rasterio.float32})

        with rasterio.open(ndvi_file_path, "w", **meta) as ndvi_file:
            ndvi_file.write(ndvi_result, 1)
        with rasterio.open(rgb_file_path, "w", **meta) as rgb_file:
            rgb_file.write(rgb_result, (1, 2, 3))

        try:
            cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}--NDVI--{img_date}", data=ndvi_file_path)
            cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}--RGB--{img_date}", data=rgb_file_path)
        except ConflictingDataError as e:
            logger.error(e)

    region.dates = dates
    region.date_last_download = datetime.strptime(last_image_date, '%Y-%m-%d')
    region.save(update_fields=["dates", "date_last_download"])


@shared_task()
def get_new_images():
    """
        Step 1: Get target regions( region.date_last_download is less than or equals to 7 days ago )
        Step 2: Slice regions to smaller and nested list: [1,2,3,4,5,6,7] -> [[1,2,3], [4,5,6], [7]]
        Step 3: Call download_images for every region in sliced_regions(Step2) and get task.id
        Step 4: Download every small region list images and wait until state != PENDING
        STEP 5: Check that tasks are done without FAILURE states
        STEP 6: Check that tasks are done with SUCCESS states
        ** DONE **
    """
    logger.info("Start task -> get_new_images")
    date_today = datetime.today()
    regions = Region.objects \
        .filter(date_last_download__lte=date_today - timedelta(days=7)) \
        .only("id", "user_id", "polygon", "dates")  # Step 1
    mdipt = getattr(settings, "MAXIMUM_DOWNLOAD_IMAGE_PER_TASK", 3)
    sliced_regions = [regions[i:i + mdipt] for i in range(0, len(regions), mdipt)]  # Step 2

    def get_tasks(region_list: list):
        logger.debug("get tasks")
        result = []
        for region in region_list:
            start_str = (region.date_last_download + timedelta(days=1)).strftime('%Y-%m-%d')
            end_str = date_today.strftime('%Y-%m-%d')
            task = download_images.delay(start=start_str, end=end_str, dates=region.dates,
                                         polygon_geojson=get_geojson_by_polygon(region.polygon),
                                         user_id=region.user_id, region_id=region.id)
            result.append(task)
        return result

    for region_slice in sliced_regions:
        tasks_list = get_tasks(region_slice)  # Step 3
        while all(AsyncResult(task.id).state != "PENDING" for task in tasks_list):  # Step 4
            sleep(1)

        if any(AsyncResult(task.id).state == "FAILURE" for task in tasks_list):  # Step 5
            # Check if state is FAILURE for any task in the tasks_list.
            for task in tasks_list:
                async_result = AsyncResult(task.id)
                if async_result.state == "FAILURE":
                    logger.error(f"Task with ID={task.id} is failed. Result={async_result.result}")
                    raise TaskError()
        elif any(AsyncResult(task.id).state != "SUCCESS" for task in tasks_list):  # Step 6
            # Check if state is not SUCCESS for any task in the tasks_list.
            for task in tasks_list:
                async_result = AsyncResult(task.id)
                if async_result.state != "SUCCESS":
                    logger.error(f"Task with ID={task.id} is not success. Result={async_result.result}")
                    raise TaskError()


def call_download_images_celery_task(instance: Region):
    end = datetime.now()
    start = end - timedelta(days=30)
    geom = get_geojson_by_polygon(instance.polygon)
    args = (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
            geom, instance.user_id, instance.id, instance.dates)
    task = celery_app.send_task("download_images", args)
    return task
