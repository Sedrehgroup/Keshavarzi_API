import json
from datetime import datetime, timedelta

from django.contrib.gis.geos import Polygon
from rest_framework.exceptions import ValidationError

from config import celery_app
from regions.models import Region


def get_polygon_by_geojson(geojson) -> Polygon:
    features = geojson["features"][0]
    coordinates = features["geometry"]["coordinates"][0]
    if len(coordinates) == 0:
        raise ValidationError({"Invalid coordinates": "Coordinates is empty"})
    return Polygon(coordinates)


def get_geojson_by_polygon(polygon: Polygon = None, convert_json=False, properties={}):
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[lat, long] for lat, long in polygon.coords[0]]]
                }
            }
        ]
    }
    if convert_json:
        return json.dumps(data)
    return data


def call_download_images_celery_task(instance: Region):
    end = datetime.now()
    start = end - timedelta(days=30)
    geom = get_geojson_by_polygon(instance.polygon)
    args = (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'),
            geom, instance.user_id, instance.id, instance.dates)
    task = celery_app.send_task("download_images", args)
    return task
