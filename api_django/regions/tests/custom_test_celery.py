# How to run this test:
#    python manage.py test regions.tests.custom_test_celery --settings=config.settings.test --keepdb
import os

from time import sleep
from celery.result import AsyncResult
from django.test.testcases import SimpleTestCase
from ee.apitestcase import ApiTestCase
from rest_framework import status
from rest_framework.reverse import reverse

from regions.models import Region
from regions.tests.factories import RegionFactory, fake_polygon
from regions.utils import get_polygon_by_geojson
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")


def RUR_URL(region_id):
    """ Retrieve Update Region URL """
    return reverse("regions:retrieve_update_region", kwargs={"pk": region_id})


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


class BaseRegionViewsTestCase(ApiTestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword123#@!"
        self.user = UserFactory.create(password=self.password)
        self.admin = AdminFactory.create(password=self.password)
        self.expert = ExpertFactory.create(password=self.password)
        self.region = RegionFactory.create(with_expert=False)

    def login(self, phone_number, password=None):
        password = password if password is not None else self.password
        data = {"phone_number": phone_number, "password": password}
        res = self.client.post(LOGIN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK, f"{res.data}\ncredential => {data}")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data['access'])
        return self


class UpdateRegion(BaseRegionViewsTestCase):
    def test_update_region_with_user(self):
        region = RegionFactory.create(user=self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of Region
                3- Update region
            """
            data = {"name": "Update test name"}
            res = self.client.patch(RUR_URL(region.id), data)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        region.refresh_from_db()
        self.assertEqual(region.name, "Update test name")

    def test_update_region_with_admin(self):
        region = RegionFactory.create()
        self.login(self.admin.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of Region
                3- Update region
            """
            data = {"name": "Update test name"}
            res = self.client.patch(RUR_URL(region.id), data)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        region.refresh_from_db()
        self.assertEqual(region.name, "Update test name")

    def test_update_region_with_expert(self):
        region = RegionFactory.create(expert=self.expert)
        region_name = region.name
        self.login(self.expert.phone_number)

        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            data = {"name": "Update test name"}
            res = self.client.patch(RUR_URL(region.id), data)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        region.refresh_from_db()
        self.assertEqual(region.name, region_name)

    def test_update_not_matched_region_to_user(self):
        region = RegionFactory.create()
        region_name = region.name
        RegionFactory.create(user=self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            data = {"name": "Update test name"}
            res = self.client.patch(RUR_URL(region.id), data)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)
        region.refresh_from_db()
        self.assertEqual(region.name, region_name)

    def test_update_not_matched_region_to_expert(self):
        region = RegionFactory.create(with_expert=True)
        region_name = region.name
        RegionFactory.create(expert=self.expert)
        self.login(self.expert.phone_number)


        data = {"name": "Update test name"}
        res = self.client.patch(RUR_URL(region.id), data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        region.refresh_from_db()
        self.assertEqual(region.name, region_name)

    def test_dates_field_is_not_updatable(self):
        self.login(self.user.phone_number)
        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            data = {"dates": "invalid_dates"}
            res = self.client.patch(RUR_URL(self.region))
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, res.data)
        self.region.refresh_from_db()
        self.assertNotEqual(self.region.dates, data["dates"])


class RetrieveRegion(BaseRegionViewsTestCase):
    def test_retrieve_region_by_user(self):
        region = RegionFactory.create(expert=self.expert)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_retrieve_region_by_expert(self):
        region = RegionFactory.create(expert=self.expert)
        self.login(self.expert.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_retrieve_region_by_admin(self):
        self.login(self.admin.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(self.region.id))
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_retrieve_region_by_not_related_user(self):
        region = RegionFactory.create()
        self.assertEqual(region.user, self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_retrieve_region_by_not_related_expert(self):
        region = RegionFactory.create(with_expert=True)
        self.assertEqual(region.expert, self.expert)
        self.login(self.expert.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_polygon_of_region_is_valid_geojson(self):
        region = RegionFactory.create(user=self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertIn('polygon', res.data)
        get_polygon_by_geojson(res.data["polygon"])

    def test_schema_of_response(self):
        region = RegionFactory.create(user=self.user)
        self.login(self.user.phone_number)
        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(region.id))
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertIn("name", res.data)
        self.assertIn("polygon", res.data)
        self.assertIn("dates", res.data)
        self.assertIn("is_active", res.data)

    def test_endpoint_with_not_exists_region(self):
        invalid_region_id = Region.objects.order_by('id').only("id").last().id + 1
        self.login(self.user.phone_number)
        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(RUR_URL(invalid_region_id))
            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, res.data)
