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

    # def test_get_regions_id_date(self):
    #     date_range = ("2021-01-01", "2021-02-01")
    #     geom = {
    #         "type": "FeatureCollection",
    #         "features": [
    #             {
    #                 "type": "Feature",
    #                 "properties": {},
    #                 "geometry": {
    #                     "coordinates": [
    #                         [
    #                             [
    #                                 51.38587730337923,
    #                                 35.705011566456065
    #                             ],
    #                             [
    #                                 51.38587730337923,
    #                                 35.68850620569404
    #                             ],
    #                             [
    #                                 51.410752479782275,
    #                                 35.68850620569404
    #                             ],
    #                             [
    #                                 51.410752479782275,
    #                                 35.705011566456065
    #                             ],
    #                             [
    #                                 51.38587730337923,
    #                                 35.705011566456065
    #                             ]
    #                         ]
    #                     ],
    #                     "type": "Polygon"
    #                 }
    #             }
    #         ]
    #     }
    #
    #     id_date_list = utils.get_regions_id_date(geom, date_range)
    #     self.assertEqual(len(id_date_list), 6)

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
        with_underline = ("2022_02_01", "2022_03_01")
        without_zero = ("2022-2-1", "2022-3-1")
        in_date_format = (datetime.now(), datetime.now() - timedelta(days=30))

        func = utils.get_and_validate_date_range
        self.assertEqual(without_zero, func(*without_zero))
        self.assertRaises(ValidationError, lambda: func(*with_underline))
        self.assertRaises(ValidationError, lambda: func(*in_date_format))

    def test_date_of_image_collection(self):
        """ Test that this function is return list of [ID, Image_name] of every image that exists in image collection """
        image_collection = utils.get_image_collections(self.gee_polygon, self.start, self.end)
        result = utils.get_dates_of_image_collection(image_collection)

        self.assertEqual(sum(1 for _ in result), 6)