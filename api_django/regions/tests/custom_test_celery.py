# How to run this test:
#    python manage.py test regions.tests.custom_test_celery --settings=config.settings.test --keepdb
import os

from time import sleep
from celery.result import AsyncResult
from django.test.testcases import SimpleTestCase

from regions.models import Region
from regions.tests.factories import fake_polygon
from users.tests.factories import UserFactory


class CeleryTasksTestCase(SimpleTestCase):
    databases = ("default",)

    def setUp(self):
        self.user = UserFactory.create()
        self.region = Region.objects.create(user_id=self.user.id, polygon=fake_polygon, name="test polygon")
        res = AsyncResult(self.region.task_id)

        while res.state == "PENDING":
            sleep(2)

        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")

        self.region.refresh_from_db()

    def tearDown(self) -> None:
        self.user.delete()

    def test_create_method_is_calling_download_image_signal(self):
        self.assertIsNotNone(self.region.task_id)

    def test_create_is_update_dates_field(self):
        self.assertIsNotNone(self.region.dates)
        self.assertTrue(len(self.region.dates.split("\n")) > 1)

    def test_create_is_save_images_in_directory(self):
        for image_path in self.region.images_path:
            self.assertTrue(os.path.isfile(image_path))

    def test_delete_images_after_delete_region(self):
        """ Test that images of the region will be deleted after the region is deleted. """
        images_path = self.region.images_path
        self.region.delete()

        for image_path in images_path:
            self.assertFalse(os.path.isfile(image_path))
