import time

import rasterio
import requests
import ee
import os

from django.conf import settings
from django.utils.timezone import now
from regions.tests.factories import fake_polygon_geojson


# https://gis.stackexchange.com/questions/429958/calculating-monthly-modis-ndvi-using-gee-python-api-applied-to-one-or-multiple-r
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://gis.stackexchange.com/questions/302847/creating-subset-of-tiff-image-and-generating-its-ndvi-in-python
# NDVI => Normalized Difference Vegetation Index
# NDVI = (Band 8 – Band 4) / (Band 8 + Band 4)

def download_image_all_bands(image: ee.Image, polygon):
    url = image.getDownloadURL(params={
        'scale': 10, "bands": ['TCI_R', 'TCI_G', 'TCI_B', 'B8', 'B4'], 'region': polygon,
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    folder_path = f"{settings.BASE_DIR}/{'/'.join(['media', 'images', 'test', 'all', now().strftime('%Y-%m-%d_%H-%M-%S')])}"
    os.makedirs(folder_path, exist_ok=True)
    file_path = f"{folder_path}/file.tif"

    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(file_path, 'wb') as raster_file:
            raster_file.write(response.content)
    return file_path, folder_path


def download_ndvi(image: ee.Image, polygon, folder_path):
    url = image.normalizedDifference(['B8', 'B4']).getDownloadURL(params={
        'scale': 10, 'region': polygon,
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    file_path = f"{folder_path}/ndvi.tif"

    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(file_path, 'wb') as ndvi_file:
            ndvi_file.write(response.content)

    return file_path


def download_image_rgb_band(image: ee.Image, polygon, folder_path):
    url = image.getDownloadURL(params={
        'scale': 10, "bands": ['TCI_R', 'TCI_G', 'TCI_B'], 'region': polygon,
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    file_path = f"{folder_path}/rgb.tif"
    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(file_path, 'wb') as rgb_file:
            rgb_file.write(response.content)

    return file_path


def download_one_image():
    """ Download one image and then get NDVI with rasterio """
    st = time.time()
    polygon = ee.Geometry.Polygon(coords=fake_polygon_geojson['features'][0]['geometry']['coordinates'])
    image = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterBounds(polygon) \
        .filterDate('2022-11-05', '2022-11-12') \
        .first()

    file_path, folder_path = download_image_all_bands(image, polygon)
    with rasterio.open(file_path, 'r') as data:
        b8, b4 = data.read(4), data.read(5)  # ['TCI_R', 'TCI_G', 'TCI_B', 'B8', 'B4']
        ndvi_result = (b8 - b4) / (b8 + b4)

        meta = data.meta
        meta.update(driver='GTiff')
        meta.update(dtype=rasterio.float32)
    ndvi_file_path = f"{folder_path}/NDVI.tif"
    with rasterio.open(ndvi_file_path, 'w', **meta) as ndvi_file:
        ndvi_file.write(ndvi_result, 1)

    elapsed_time = time.time() - st
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print(f"NDVI size file -> {os.path.getsize(ndvi_file_path)}")
    print(f"RPG size file -> {os.path.getsize(file_path)}")

    return elapsed_time
# Download all images       -> 2.8836936950683594 second -> NDVI:4602750 bytes    RGB:1321225 bytes
# Download seperated images -> 5.1786751985549930 secnod -> NDVI:6922750 bytes    RGB:4876400 bytes

def download_two_image():
    """ Download RGB and NDVI separately """
    st = time.time()
    polygon = ee.Geometry.Polygon(coords=fake_polygon_geojson['features'][0]['geometry']['coordinates'])
    image = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterBounds(polygon) \
        .filterDate('2022-11-05', '2022-11-12') \
        .first()

    folder_path = f"{settings.BASE_DIR}/{'/'.join(['media', 'images', 'test', 'seperated', now().strftime('%Y-%m-%d_%H-%M-%S')])}"
    os.makedirs(folder_path, exist_ok=True)
    file_ndvi_path = download_ndvi(image, polygon, folder_path)
    file_rgb_path = download_image_rgb_band(image, polygon, folder_path)

    elapsed_time = time.time() - st
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print(f"NDVI size file -> {os.path.getsize(file_ndvi_path)}")
    print(f"RPG size file -> {os.path.getsize(file_rgb_path)}")

    return elapsed_time


def download_test():
    list_all = []
    for _ in range(20):
        list_all.append(download_one_image())

    list_seperated = []
    for _ in range(20):
        list_seperated.append(download_two_image())

    print(f"Download all images -> {sum(list_all) / len(list_all)}")
    print(f"Download seperated images -> {sum(list_seperated) / len(list_seperated)}")


if __name__ == "__main__":
    download_test()