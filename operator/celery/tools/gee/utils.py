import json
import logging
import ee
import os

from pathlib import Path
from typing import Tuple
from datetime import datetime, date
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve()
private_key_path = os.path.join(settings.BASE_DIR, "utils", "gee", "geotest-privkey.json")
if not os.path.isfile(private_key_path):
    raise FileNotFoundError("geotest-privkey.json not found. This file should exists in utils.gee package.")

service_account = 'geo-test@geotest-317218.iam.gserviceaccount.com'
with open(private_key_path, 'r') as pk:
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json.dumps(json.load(pk)))
ee.Initialize(credentials)


class RegionTools:
    def __init__(self, user_id, region_id, dates):
        self.user_id = user_id
        self.region_id = region_id
        self.dates = dates

    def dates_as_list(self):
        dates_list = self.dates.split("\n")  # ['2021-01-02', '']
        dates_list.pop()  # Pop the last and empty value
        return dates_list

    def user_folder_path(self):
        return f"{BASE_DIR}/{'/'.join(['media', 'images', f'user-{str(self.user_id)}'])}"

    def folder_path(self):
        return f"{BASE_DIR}/{'/'.join(['media', 'images', f'user-{str(self.user_id)}', f'region-{str(self.region_id)}'])}"

    def create_ndvi_rgb_dir(self):
        import os
        os.makedirs(f"{self.folder_path}/ndvi", exist_ok=True)
        os.makedirs(f"{self.folder_path}/rgb", exist_ok=True)

    def get_ndvi_path(self, image_date):
        return f"{self.folder_path}/ndvi/{image_date}.tif"

    def get_list_ndvi_path(self):
        folder_path = self.folder_path
        result = []
        for image_date in self.dates_as_list():
            result.append(f"{folder_path}/ndvi/{image_date}.tif")

    def get_rgb_path(self, image_date):
        return f"{self.folder_path}/rgb/{image_date}.tif"

    def get_list_rgb_path(self):
        folder_path = self.folder_path
        result = []
        for image_date in self.dates_as_list():
            result.append(f"{folder_path}/rgb/{image_date}.tif")


def get_and_validate_date_range(start_date: str, end_date: str) -> Tuple[date, date]:
    logger.debug("Get and validate date range")
    try:
        # 1- Validate that input strings are in a correct format.
        # 2- Convert string-datetime to datetime instance.
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        return start_date, end_date
    except (ValueError, TypeError) as e:
        # Exception message example: time data '12/11/2018' does not match format '%Y-%m-%d'
        raise ValueError({"msg": e, "values": (start_date, end_date)})


def get_dates_of_image_collection(image_collection: ee.ImageCollection):
    logger.debug("Get dates of image collection")
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
    logger.debug("Get image collection")
    """Get image collection by given polygon that are took between validated start and end date"""
    return ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterDate(start, end) \
        .filterBounds(polygon)


def get_and_validate_polygon_by_geom(polygon_geojson) -> ee.Geometry.Polygon:
    logger.debug("Get and validate polygon by geom")
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
    logger.debug("Get clipped image")
    try:
        return ee.Image(image_name).clip(polygon).select(['TCI_R', 'TCI_G', 'TCI_B'])
    except Exception as e:
        raise ValidationError({"function name": "get_clipped_image", "message": e})
