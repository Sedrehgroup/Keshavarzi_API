import json
import logging
import os
from typing import Tuple, Union

import ee

from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

key_data = {
    "type": "service_account",
    "project_id": "geotest-317218",
    "private_key_id": "0f39d992671e61c7c3d4e62b33fc1ac28ad4df59",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCfYkoznQxVt09s\nOw+E/0PbZi42Hr6sy0OUm2I+BxvK7FYSDApZXzKKaOoee/xzNK56UV/2rXKAXs6M\nJvUWDygBx0QK+edeV+lVst5M2bbedf+p169yH57E2QJuPOdqcUErUagh/jKQOlYB\nn62kknb+iRlvmYC3zPyYxRh8sxz4+xLhvOFhkorwk1aAO9fG7Ivt8Fob6bZ1j55M\ngbjoH3gfZSNTpaYzvvDgtL4G8IE1j4USrXlMT2s13p9Z4Bz1oQe2DmH1VErhXAo7\ntieKgCELxSJSYawDvQ4e8m9lmB8NgPMSAdM3nRVep02BDFbZ8u31fEHLLWbzJewB\nLyG+sJCJAgMBAAECggEAIBeecT4SGcBLUbOisFjlxOuSKnuOUSSseuO+qFauFfH4\ncrHR86TjfFMbsP+uGVRmPWLdO8I45/gvBrFhcAulNpZ08PDY0XpKFWNqt3avB6Qi\n0oQHY6dSRLidcKz6u8gKIzrR6+ZPMBNO9gy83gJPy3i3km0KKfgwdGJbR+CY2NkD\n0/jFEQQa35lLVp8LqoXPn1Rohwg2urLT2Xdb2DOWxRedKSHelilnceRPGYkNEwMB\nueb+hxhyKFM3LdwHQZ4R1vGqflBzl2GUy63pZawb+j+KhYOfeYJ02RAcFn1kLId8\nqxvTwogeaFZ9EPSg53SqpFs2u3lmU0iKCXpBz/Ug8QKBgQDQ6fziGB0AOyp6JyxI\nZYg5Hb7bHgbUcGXRR/rf92YsRtnB6s4n1eIw5zy5g6xalB19hNBILFipWZc7zYAO\nPOw5GWfFtpQqbx5CU4uxTzCur6oxzQBDTa74L0c1Vm0TDnbMT9y2OG66Iu2Djx9B\nG4n0FWAIf+uQWQ+x0aQsRp7jrwKBgQDDTn6PlkJ70LinRYmAc3GhAt11dTg1Okng\npQR0iQ/qwYdhFayWMGOp8zAkNw+QyQT8+6csqUHFfh/Spk8Kp4f3GVzJGQ7Ggw7A\nlo53Z1uFK7FP3ru3JF0dFayGDl0L9YBjs3gWvjubjeLPxpfEawm4mDeiT62C2+m8\nvwSl9uMFRwKBgQCWO/5gNQj99o5YY71Dnsg0ksCCYHh24xFFS+cMkqQGKTlFa26v\nVO8hTdjsa9VRGfyPHCiQDlwABO5t0h1Jn+QcN7nZg6/PSDNRbTUi4BjZNnhE8fBD\ndiTiU1V49NrhfmBOEwxcef6emqmFFzJZps0xGwIBesRS/Mj9jg3qzSpL/wKBgA32\n+NmvdsV/oRRkxnYmywMmP0t8vC4iItIrOmxSuI6ik9l/QT3j69xlBRYx0a0akn68\nR7HL0GYcpI3dUl2CqRgj+hxu7D2JdW6T1U/4VfTpsN3zIRzxPq8rs5BKSqDmRu3a\nEUYfCAgRVxxgKM3kkWdfiurSI6ftrYLPbbeoNYdVAoGAIdUK2S2JA0Hnpw4oA3ur\nOekguTVj+hMELCu5qaqIUQxVWNBamCZ2qgGs+fbSD0jb3OtyoAK0rvfCJyTTWya8\nbJOwUhwX1ryNvtS+OuO5Wt+5ad/ND62BRM9tUK5w3Iiu6vl3pov2XXWzyyjIi92t\nD2swZ7vpifOSq/e9Dsk2Qls=\n-----END PRIVATE KEY-----\n",
    "client_email": "geo-test@geotest-317218.iam.gserviceaccount.com",
    "client_id": "103258789032168134822",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/geo-test%40geotest-317218.iam.gserviceaccount.com"
}
service_account = 'geo-test@geotest-317218.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, key_data=json.dumps(key_data))
logger.info("Initialize Google earth engine ")
ee.Initialize(credentials)
logger.info("Google earth engine is Initialized")


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
