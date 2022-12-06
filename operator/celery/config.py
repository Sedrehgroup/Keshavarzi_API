import os
import logging
import ee
import rasterio
import requests

from io import BytesIO
from celery import Celery
from celery.exceptions import InvalidTaskError
from datetime import timedelta
from geoserver.catalog import ConflictingDataError

from tools.geoserver.base import cat
from tools.gee.utils import get_and_validate_polygon_by_geom, get_image_collections, \
    get_dates_of_image_collection, RegionTools

logger = logging.getLogger(__name__)

celery_app = Celery('config')

celery_app.conf.broker_url = f"amqp://{os.environ['RABBITMQ_DEFAULT_USER']}:{os.environ['RABBITMQ_DEFAULT_PASS']}@{os.environ['RABBITMQ_IP']}"
celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 1


@celery_app.task
def download_images(start, end, polygon_geojson, user_id, region_id, dates):
    """
        ** Note**
        start: str -> example: "2022-01-01"
        end: str   -> example: "2022-01-01"
    """
    logger.debug("Start task -> download_images")
    try:
        polygon = get_and_validate_polygon_by_geom(polygon_geojson)
    except Exception as e:
        logger.error(e)
        raise InvalidTaskError(e)

    image_collection = get_image_collections(polygon, start, end)
    id_date_list = get_dates_of_image_collection(image_collection)
    region_tools = RegionTools(user_id, region_id, dates)

    region_tools.create_ndvi_rgb_dir()
    dates = dates if dates else ""
    logger.debug("Start downloading images")
    for img_id, img_date in id_date_list:
        logger.debug(f"Start image with {img_date} date")
        url = ee.Image(img_id).getDownloadURL(params={
            'scale': 10, 'region': polygon,
            "bands": ['TCI_R', 'TCI_G', 'TCI_B', 'B4', 'B8'],
            'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

        ndvi_file_path = region_tools.get_ndvi_path(img_date)  # Example: /media/images/user-1/region-1/ndvi/2022-01-02.tif
        rgb_file_path = region_tools.get_rgb_path(img_date)  # Example: /media/images/user-1/region-1/rgb/2022-01-02.tif
        dates += f"{img_date}\n"
        logger.debug("Start downloading")
        with requests.get(url) as response:
            logger.debug("End downloading")
            with BytesIO(response.content) as content:
                with rasterio.open(content) as raster_file:
                    b4, b8 = raster_file.read(4), raster_file.read(5)  # ['TCI_R', 'TCI_G', 'TCI_B', 'B4', 'B8']
                    b4 = b4.astype('float16')  # ToDo: Delete this line and change format of gee image
                    b8 = b8.astype('float16')  # ToDo: Delete this line and change format of gee image
                    ndvi_result = (b8 - b4) / (b8 + b4)
                    rgb_result = raster_file.read((1, 2, 3))

                    meta = raster_file.meta
                    meta.pop("count")
                    meta.update({"width": raster_file.width, "height": raster_file.height,
                                 "driver": 'GTiff', "dtype": rasterio.uint8})
        with rasterio.open(ndvi_file_path, "w", **meta, count=1) as ndvi_file:
            logger.debug("Write NDVI file")
            ndvi_file.write(ndvi_result, 1)
        with rasterio.open(rgb_file_path, "w", **meta, count=3) as rgb_file:
            logger.debug("Write RGB  file")
            rgb_file.write(rgb_result, (1, 2, 3))

        try:
            logger.debug("Send NDVI file to geoserver")
            cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}--NDVI--{img_date}", data=ndvi_file_path)
            logger.debug("Send RGB file to geoserver")
            cat.create_coveragestore(name=f"user_{user_id}--region_{region_id}--RGB--{img_date}", data=rgb_file_path)
        except ConflictingDataError as e:
            logger.error(e)
        logger.debug("END sending files")
