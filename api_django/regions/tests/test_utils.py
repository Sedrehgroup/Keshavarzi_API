import ee
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from datetime import datetime, timedelta

from regions.tests.factories import fake_polygon_geojson
from utils.gee import utils


class RegionUtilsTestCase(APITestCase):
    def setUp(self) -> None:
        self.gee_polygon = ee.Geometry.Polygon(coords=fake_polygon_geojson['features'][0]['geometry']['coordinates'])
        self.start, self.end = ("2022-02-01", "2022-03-01")

    def test_geom_validation(self):
        """ Test that get_and_validate_polygon_by_geom is working as expected """
        without_features = {"type": "FeatureCollection"}
        empty_features = {"type": "FeatureCollection", "features": []}
        empty_geometry = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {}}]}
        empty_coordinates = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"coordinates": [
        ], "type": "Polygon"}}]}

        func = utils.get_and_validate_polygon_by_geom
        self.assertRaises(ValidationError, lambda: func(without_features))
        self.assertRaises(ValidationError, lambda: func(empty_features))
        self.assertRaises(ValidationError, lambda: func(empty_geometry))
        self.assertRaises(ValidationError, lambda: func(empty_coordinates))

    def test_date_validation(self):
        """ Test that invalid date format is raise exception """
        valid_str = ("2022-02-01", "2022-03-01")
        valid_date = (datetime.strptime("2022-02-01", '%Y-%m-%d'), datetime.strptime("2022-03-01", '%Y-%m-%d'))
        with_underline = ("2022_02_01", "2022_03_01")
        without_zero = ("2022-2-1", "2022-3-1")

        func = utils.get_and_validate_date_range
        self.assertEqual(valid_str, func(*valid_date))
        self.assertEqual(valid_str, func(*valid_str))
        self.assertEqual(valid_str, func(*without_zero))
        self.assertRaises(ValidationError, lambda: func(*with_underline))

    def test_date_of_image_collection(self):
        """ Test that this function is return list of [ID, Image_name] of every image that exists in image collection """
        image_collection = utils.get_image_collections(self.gee_polygon, self.start, self.end)
        result = utils.get_dates_of_image_collection(image_collection)

        self.assertEqual(sum(1 for _ in result), 6)
