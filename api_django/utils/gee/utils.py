import json
import logging
import os
from typing import Tuple

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

if not os.path.isdir(os.path.join(settings.BASE_DIR, 'images')):
    os.mkdir(os.path.join(settings.BASE_DIR, 'images'))


def get_and_validate_date_range(start_date: str, end_date: str) -> Tuple[str, str]:
    logger.info("Get and validate date range")
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except (ValueError, TypeError)  as e:
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


def get_and_validate_polygon_by_geom(geom) -> ee.Geometry.Polygon:
    logger.info("Get and validate polygon by geom")
    """
        Convert geom to Polygon.
        Hint: If geom is not the type of geojson -> raise BadRequest
    """
    try:
        return ee.Geometry.Polygon(geom['features'][0]['geometry']['coordinates'])
    except Exception as e:
        raise ValidationError({"function name": "get_and_validate_polygon_by_geom", "message": e, "geom_data": geom})


def get_clipped_image(image_name, polygon: ee.Geometry.Polygon) -> ee.Image:
    logger.info("Get clipped image")
    try:
        return ee.Image(image_name).clip(polygon).select(['TCI_R', 'TCI_G', 'TCI_B'])
    except Exception as e:
        raise ValidationError({"function name": "get_clipped_image", "message": e})

# def turn_image_to_raster(image: ee.Image, title, polygon: ee.Geometry.Polygon) -> None:
#     # download image from google earth engine
#     # ToDo: What if image is not exists?
#     folder = os.path.join(settings.BASE_DIR, 'images/')
#     url = image.getDownloadURL(params={
#         'name': title, 'scale': 10, 'region': polygon,
#         'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})
#
#     if not os.path.exists(folder):
#         os.mkdir(folder)
#
#     with requests.get(url) as response:
#         with open(folder + title + '.tif', 'wb') as raster_file:
#             # ToDo: Test without wb
#             raster_file.write(response.content)


# def add_layer(layer_name) -> None:
#     filename = layer_name + '.tif'
#     if not exist_layer(layer_name, settings.GEOSERVER.get('WORKSPACE')):
#         create_layer_with_store(data_type='tiff', layer_name=layer_name, store_name=layer_name,
#                                 url=os.path.join(settings.GEOSERVER.get('RASTER_URL'), filename))


# geom = {
#   "type": "FeatureCollection",
#   "features": [
#     {
#       "type": "Feature",
#       "properties": {},
#       "geometry": {
#         "type": "Polygon",
#         "coordinates": [
#           [
#             [
#               51.840362548828125,
#               35.74386509767359
#             ],
#             [
#               51.847829818725586,
#               35.74386509767359
#             ],
#             [
#               51.847829818725586,
#               35.74922899279072
#             ],
#             [
#               51.840362548828125,
#               35.74922899279072
#             ],
#             [
#               51.840362548828125,
#               35.74386509767359
#             ]
#           ]
#         ]
#       }
#     }
#   ]
# }
# order_id = '1'
# image_class = GetImage(start = '2020-01' , end = '2020-02' , polygon = geom)
# image_names , image_dates = image_class.get_dates()
# print(image_dates)
# for item in image_names:
#   image = image_class.get_image(item)
#   image_class.turn_image_to_raster(image,order_id + '_' + item,image_class.polygon,)


# def format_convert(path, filename, format):
#     # path = os.path.join(settings.BASE_DIR , 'images')
#     if format == 'tif':
#         file_format = '.tif'
#     else:
#         # tif to jpeg
#         source_file = cv2.imread(path + filename + '.tif')
#         target_file = cv2.imwrite(path + filename + '.jpg', source_file)
#         file_format = '.jpg'
#
#     target_file_path = path + filename + file_format
#
#     target_file_path_zip = path + filename + '.zip'
#     with ZipFile(target_file_path_zip, 'w') as zip_file:
#         zip_file.write(target_file_path, basename(target_file_path))
#
#     return target_file_path_zip


# def add_image_to_geoserver(image_name: str, geom: list) -> str:
#     # ToDo: Set a good docstring for this function
#     polygon = get_and_validate_polygon_by_geom(geom)
#
#     image: ee.Image = get_clipped_image(image_name, polygon)
#     layer_name = str(123) + '_' + image_name  # ToDo: Replace 123 with random or remove it
#
#     turn_image_to_raster(image, layer_name, polygon)
#
#     if not exist_layer(layer_name, settings.GEOSERVER.get('WORKSPACE')):
#         url = os.path.join(settings.GEOSERVER.get('RASTER_URL'), layer_name + ".tif")
#         create_layer_with_store(data_type='tiff', url=url, layer_name=layer_name, store_name=layer_name)
#
#     return layer_name


# def get_regions_id_date(geom, date_range: Tuple[str, str]) -> list:
#     """ Save every image of geom by using the celery """
#     # ToDo: Test that date_range validator is working
#     # if not isinstance(start_date, str) or not isinstance(end_date, str):
#     #     return Response(status=status.HTTP_400_BAD_REQUEST, data={"fail": "dates not correct!"})
#     start, end = get_and_validate_date_range(date_range)
#     polygon = get_and_validate_polygon_by_geom(geom)
#
#     image_collection = get_image_collections(polygon, start, end)
#     id_date_list = get_dates_of_image_collection(image_collection)
#
#     return id_date_list
