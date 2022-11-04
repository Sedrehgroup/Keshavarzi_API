import os

from time import sleep
from celery.result import AsyncResult
from django.test.testcases import SimpleTestCase

from regions.models import Region
from regions.tests.factories import fake_polygon
from users.tests.factories import UserFactory

#Test
class CeleryTasksTestCase(SimpleTestCase):
    databases = ("default",)

    @classmethod
    def setUpClass(cls):
        cls.user = UserFactory.create()
        cls.region = Region.objects.create(user_id=cls.user.id, polygon=fake_polygon, name="test polygon")
        res = AsyncResult(cls.region.task_id)

        while res.state == "PENDING":
            sleep(2)

        cls.assertNotEqual(res.state, "FAILURE", res.result)
        cls.assertEqual(res.state, "SUCCESS")

        cls.region.refresh_from_db()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.user.delete()

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
