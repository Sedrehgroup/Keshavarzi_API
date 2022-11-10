import os
from time import sleep

from celery.result import AsyncResult
from celery.contrib.testing.worker import start_worker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APISimpleTestCase

from config.celery import celery_app
from regions.models import Region
from regions.tests.factories import RegionFactory, fake_polygon_geojson, fake_polygon_geojson_2
from regions.utils import get_polygon_by_geojson
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")
CREATE_REGION_URL = reverse("regions:create")


def RUR_URL(region_id):
    """ Retrieve Update Region URL """
    return reverse("regions:retrieve_update_region", kwargs={"pk": region_id})


class TestAfterCeleryTasks(APISimpleTestCase):
    databases = '__all__'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Start up celery worker
        cls.celery_worker = start_worker(celery_app, perform_ping_check=False)
        cls.celery_worker.__enter__()

        cls.password = "VeryStrongPassword123#@!"
        cls.user = UserFactory.create(password=cls.password)
        cls.admin = AdminFactory.create(password=cls.password)
        cls.expert = ExpertFactory.create(password=cls.password)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close worker
        cls.celery_worker.__exit__(None, None, None)

    def login(self, phone_number, password=None):
        password = password if password is not None else self.password
        data = {"phone_number": phone_number, "password": password}
        res = self.client.post(LOGIN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK, f"{res.data}\ncredential => {data}")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data['access'])
        return self

    def test_that_dates_field_is_not_empty(self):
        region = RegionFactory.create(user=self.user)
        res = AsyncResult(region.task_id)
        while res.state == "PENDING":
            sleep(1)
        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")

        self.login(self.user.phone_number)
        res = self.client.get(RUR_URL(region.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertIn("dates", res.data)
        self.assertIsNotNone(res.data["dates"])

    def test_update_images_after_update_polygon(self):
        region = RegionFactory.create(user=self.user)
        old_res = AsyncResult(region.task_id)
        old_date_last_download = region.date_last_download
        old_task_id = region.task_id
        while old_res.state == "PENDING":
            sleep(1)
        self.assertNotEqual(old_res.state, "FAILURE", old_res.result)
        self.assertEqual(old_res.state, "SUCCESS")
        self.login(self.user.phone_number)

        data = {"polygon": fake_polygon_geojson_2}
        res = self.client.patch(RUR_URL(region.id), data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        region.refresh_from_db()

        self.assertNotEqual(region.task_id, old_task_id)
        self.assertNotEqual(region.date_last_download, old_date_last_download)

        res = AsyncResult(region.task_id)
        while res.state == "PENDING":
            sleep(1)
        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")
        region.refresh_from_db()

        self.assertIsNotNone(region.dates)
        for path in region.images_path:
            self.assertTrue(os.path.isfile(path))

    def test_create_region_is_download_images(self):
        self.login(self.user.phone_number)

        data = {"name": "test create region is download images", "polygon": fake_polygon_geojson}
        res = self.client.post(CREATE_REGION_URL, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        region = Region.objects.get(name=data["name"])
        res = AsyncResult(region.task_id)
        while res.state == "PENDING":
            sleep(1)
        self.assertNotEqual(res.state, "FAILURE", res.result)
        self.assertEqual(res.state, "SUCCESS")

        self.assertIsNotNone(region.dates)
        for path in region.images_path:
            self.assertTrue(os.path.isfile(path))
