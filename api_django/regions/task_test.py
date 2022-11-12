import time

import rasterio
import requests
import ee
import os

from django.conf import settings
from django.utils.timezone import now

geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              51.454203471640426,
              35.67995126888944
            ],
            [
              51.454203471640426,
              35.67993377710842
            ],
            [
              51.45422301913513,
              35.67993377710842
            ],
            [
              51.45422301913513,
              35.67995126888944
            ],
            [
              51.454203471640426,
              35.67995126888944
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}


# https://gis.stackexchange.com/questions/429958/calculating-monthly-modis-ndvi-using-gee-python-api-applied-to-one-or-multiple-r
# https://developers.planet.com/docs/planetschool/calculate-an-ndvi-in-python/
# https://gis.stackexchange.com/questions/302847/creating-subset-of-tiff-image-and-generating-its-ndvi-in-python
# NDVI => Normalized Difference Vegetation Index
# NDVI = (Band 8 – Band 4) / (Band 8 + Band 4)

def download_image_all_bands(image: ee.Image):
    url = image.getDownloadURL(params={
        'scale': 10, "bands": ['TCI_R', 'TCI_G', 'TCI_B', 'B8', 'B4'],
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    today_str = now().strftime('%Y-%m-%d_%H-%M-%S')
    print(f"download -> {today_str}")

    # Example: /media/images/test/2022-01-02/file.tif
    folder_path = f"{settings.BASE_DIR}/{'/'.join(['media', 'images', 'test', 'all', today_str])}"
    file_path = f"{folder_path}/file.tif"
    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(file_path, 'wb') as raster_file:
            raster_file.write(response.content)
    return file_path, folder_path


def download_ndvi(image: ee.Image, folder_path):
    url = image.normalizedDifference(['B8', 'B4']).getDownloadURL(params={
        'scale': 10, "bands": ['B8', 'B4'],
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    file_path = f"{folder_path}/ndvi.tif"
    print(f"download -> {file_path}")

    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(file_path, 'w') as ndvi_file:
            ndvi_file.write(response.content)

    return file_path


def download_image_rgb_band(image: ee.Image, folder_path):
    url = image.getDownloadURL(params={
        'scale': 10, "bands": ['TCI_R', 'TCI_G', 'TCI_B'],
        'crs': 'EPSG:4326', 'filePerBand': False, 'format': 'GEO_TIFF'})

    file_path = f"{folder_path}/rgb.tif"
    print(f"download -> {file_path}")
    with requests.get(url) as response:
        # Write Binary is important: https://stackoverflow.com/a/2665873/14449337
        with open(folder_path, 'w') as rgb_file:
            rgb_file.write(response.content)

    return file_path


def download_one_image():
    """ Download one image and then get NDVI with rasterio """
    st = time.time()
    image = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterBounds(ee.Geometry.Polygon(coords=geojson['features'][0]['geometry']['coordinates'])) \
        .filterDate('2022-10-05', '2022-11-12') \
        .first()


    file_path, folder_path = download_image_all_bands(image)
    with rasterio.open(file_path, 'r') as data:
        b8_4 = data.read_band((8, 4))
        b8, b4 = b8_4.read(8), b8_4.read(4)
        ndvi_result = (b8 + b4) / (b8 - b4)

    meta = b4.meta
    meta.update(driver='GTiff')
    meta.update(dtype=rasterio.float32)
    ndvi_file_path = f"{folder_path}/NDVI.tif"
    with rasterio.open(ndvi_file_path, 'w', **meta) as ndvi_file:
        ndvi_file.write(1, ndvi_result.as_type(rasterio.float32))

    elapsed_time = time.time() - st
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print(f"NDVI size file -> {os.path.getsize(ndvi_file)}")
    print(f"RPG size file -> {os.path.getsize(file_path)}")

    return elapsed_time


def download_two_image():
    """ Download RGB and NDVI separately """
    st = time.time()
    image = ee.ImageCollection("COPERNICUS/S2_SR") \
        .filterBounds(ee.Geometry.Polygon(coords=geojson['features'][0]['geometry']['coordinates'])) \
        .filterDate('2022-10-05', '2022-11-12') \
        .first()

    folder_path = f"{settings.BASE_DIR}/{'/'.join(['media', 'images', 'test', 'seperated', now().strftime('%Y-%m-%d_%H-%M-%S')])}"
    file_ndvi_path = download_ndvi(image, folder_path)
    file_rgb_path = download_image_rgb_band(image, folder_path)

    elapsed_time = time.time() - st
    print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
    print(f"NDVI size file -> {os.path.getsize(file_ndvi_path)}")
    print(f"RPG size file -> {os.path.getsize(file_rgb_path)}")

    return elapsed_time


def download_test():
    list_all = []
    for _ in range(20):
        list_all.append(download_one_image())

    print(f"Download all images -> {sum(list_all) / len(list_all)}")
    list_seperated = []
    for _ in range(20):
        list_all.append(download_two_image())

    print(f"Download seperated images -> {sum(list_seperated) / len(list_seperated)}")


if __name__ == "__main__":
    download_test()
