import json

from django.contrib.gis.geos import Polygon
from rest_framework.exceptions import ValidationError


def get_polygon_by_geojson(geojson) -> Polygon:
    features = geojson["features"][0]
    coordinates = features["geometry"]["coordinates"][0]
    print(coordinates)
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
