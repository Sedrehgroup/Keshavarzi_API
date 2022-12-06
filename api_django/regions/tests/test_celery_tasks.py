from time import sleep
from unittest import TestCase

from config import celery_app
from regions.tests.factories import RegionFactory
from regions.utils import get_geojson_by_polygon
from users.tests.factories import UserFactory

DOWNLOAD_IMAGES = "config.download_images"


class TestCeleryTasks(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        user = UserFactory.create()
        cls.user = user
        cls.region = RegionFactory.create(user=user)

    def wait_to_success(self, async_result):
        while async_result.state == "PENDING":
            sleep(1)
        if async_result.state != "SUCCESS":
            raise AssertionError({async_result.state: async_result.result})

    def test_download_image_task(self):
        """ Test that download_image task with valid data is working correctly """
        start_date = "2022-01-01"
        end_date = "2022-02-01"
        args = (start_date, end_date, get_geojson_by_polygon(self.region.polygon),
                self.user.id, self.region.id, self.region.dates)
        result = celery_app.send_task(DOWNLOAD_IMAGES, args)
        self.wait_to_success(result)
