import json
import logging
import ee
import os

from typing import Tuple, Union
from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)
private_key_path = os.path.join(settings.BASE_DIR, "utils", "gee", "geotest-privkey.json")
if not os.path.isfile(private_key_path):
    raise FileNotFoundError("geotest-privkey.json not found. This file should exists in utils.gee package.")

service_account = 'geo-test@geotest-317218.iam.gserviceaccount.com'
with open(private_key_path, 'r') as pk:
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json.load(pk))
ee.Initialize(credentials)


def get_and_validate_date_range(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> Tuple[str, str]:
    logger.info("Get and validate date range")
    date_format = '%Y-%m-%d'
    if isinstance(start_date, datetime) and isinstance(end_date, datetime):
        start_date = start_date.strftime(date_format)
        end_date = end_date.strftime(date_format)
    else:
        try:
            # Validate that input strings are in a correct format.
            datetime.strptime(start_date, date_format)
            datetime.strptime(end_date, date_format)
        except (ValueError, TypeError) as e:
            # Exception message example: time data '12/11/2018' does not match format '%Y-%m-%d'
            raise ValidationError({"datetime": e})
    return start_date, end_date


def get_dates_of_image_collection(image_collection: ee.ImageCollection):
    logger.info("Get dates of image collection")
    """
    Get image collection and return list of ID & date of images.
    Example: [(COPERNICUS/S2_SR/20210109T185751_20210109T185931_T10SEG, 2021-01-09),]
    """
    for image_features in image_collection.getInfo()['features']:
        img_id = image_features['id']  # Example -> COPERNICUS/S2_SR/20210109T185751_20210109T185931_T10SEG

        img_date = img_id.split('/')[2][:8]  # Result -> 20210109
        formatted_image_date = img_date[:4] + '-' + img_date[4:6] + '-' + img_date[6:]  # Result => 2021-01-09

        yield img_id, formatted_image_date


def get_image_collections(polygon, start, end):
    logger.info("Get image collection")
    """Get image collection by given polygon that are took between validated start and end date"""
    return ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterDate(start, end) \
        .filterBounds(polygon)


def get_and_validate_polygon_by_geom(polygon_geojson) -> ee.Geometry.Polygon:
    logger.info("Get and validate polygon by geom")
    """
        Convert geom to Polygon.
        Hint: If geom is not the type of geojson -> raise BadRequest
    """
    try:
        return ee.Geometry.Polygon(polygon_geojson['features'][0]['geometry']['coordinates'])
    except Exception as e:
        msg = {"function name": "get_and_validate_polygon_by_geom",
               "message": e, "geom_data": polygon_geojson}
        raise ValidationError(msg)


def get_clipped_image(image_name, polygon: ee.Geometry.Polygon) -> ee.Image:
    logger.info("Get clipped image")
    try:
        return ee.Image(image_name).clip(polygon).select(['TCI_R', 'TCI_G', 'TCI_B'])
    except Exception as e:
        raise ValidationError({"function name": "get_clipped_image", "message": e})
