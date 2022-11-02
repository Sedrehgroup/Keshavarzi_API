import os
from time import sleep

from celery.result import AsyncResult

from config.celery import celery_app
from regions.models import Region
from regions.tests.factories import fake_polygon
from users.tests.factories import UserFactory
from celery.contrib.testing.worker import start_worker
from django.test import SimpleTestCase


class BatchSimulationTestCase(SimpleTestCase):
    databases = '__all__'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Start up celery worker
        cls.celery_worker = start_worker(celery_app, perform_ping_check=False)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        # Close worker
        cls.celery_worker.__exit__(None, None, None)

    def test_create_method_is_calling_download_image_signal(self):
        region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test polygon")

        self.assertIsNotNone(region.task_id)

    def test_create_is_update_dates_field(self):
        region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test update dates")
        task_id = region.task_id
        res = AsyncResult(task_id)

        while res.state == "PENDING":
            sleep(5)

        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")

        region.refresh_from_db()
        self.assertIsNotNone(region.dates)
        self.assertTrue(len(region.dates.split("\n")) > 1)

    def test_create_is_save_images_in_directory(self):
        region = Region.objects.create(user_id=UserFactory.create().id, polygon=fake_polygon, name="test update dates")
        task_id = region.task_id
        res = AsyncResult(task_id)

        while res.state == "PENDING":
            sleep(5)

        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")

        region.refresh_from_db()
        self.assertIsNotNone(region.dates)
        dates_list = region.dates.split("\n")
        for date in dates_list:
            file_path = os.path.join("media", "images", f"user-{region.user_id}", f"region-{region.id}", f"{date}.tif")
            self.assertTrue(os.path.isfile(file_path))
