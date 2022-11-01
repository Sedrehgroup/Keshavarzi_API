import logging
import requests
import ee
import os
from errno import EEXIST

from celery import shared_task
from django.conf import settings

from regions.models import Region
from utils.gee.utils import get_and_validate_date_range, get_and_validate_polygon_by_geom, get_dates_of_image_collection, get_image_collections
from utils.geoserver.base import cat

logger = logging.getLogger(__name__)


def get_or_create_dir(base_dir, dir_names: list):
    logger.info("Get or create dir")
    # Recursive function for create parent directories
    try:
        os.makedirs(f"{base_dir}/{'/'.join(dir_names)}")
        return os.path.join(base_dir, *dir_names)
    except OSError as e:
        if e.errno == EEXIST:
            last_dir = dir_names.pop()
            result = get_or_create_dir(base_dir, dir_names)
            os.makedirs(f"{result}/{last_dir}")
            return os.path.join(result, last_dir)


@shared_task()
def download_images(start, end, geom, user_id, region_id, dates):
    start, end = get_and_validate_date_range(start, end)
    polygon = get_and_validate_polygon_by_geom(geom)
    folder = get_or_create_dir(settings.BASE_DIR, ["media", "images", f"user-{str(user_id)}", f"region-{str(region_id)}"])
    dates = dates if dates is not None else ""

    image_collection = get_image_collections(polygon, start, end)
    id_date_list = get_dates_of_image_collection(image_collection)

    logger.info("Start downloading images")
    for img_id, img_date in id_date_list:
        url = ee.Image(img_id).getDownloadURL(params={
            'scale': 10, 'region': polygon, "bands": ['TCI_R', 'TCI_G', 'TCI_B'],
            'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

        # Example: /media/images/user-1/region-1/2022-01-02.tif
        file_path = f"{folder}/{img_date}.tif"
        dates += f"{img_date}\n"
        with requests.get(url) as response:
            with open(file_path, 'wb') as raster_file:
                # ToDo: Test without wb
                raster_file.write(response.content)

        cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}", data=file_path)
        Region.objects.filter(id=region_id).update(dates=dates)
