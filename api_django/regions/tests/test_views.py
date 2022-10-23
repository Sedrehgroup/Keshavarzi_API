import os

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config.settings import BASE_DIR
from regions.models import Region
from regions.tests.factories import FuzzyPolygon, RegionFactory
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")
LIST_REGIONS_EXPERT_URL = reverse("regions:list_expert_regions")
LIST_REGIONS_USER_URL = reverse("regions:list_user_regions")
TEST_TIF = os.path.join(BASE_DIR, "regions", "tests", "test.tif")


class RegionViewsTestCase(APITestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword123#@!"
        self.regular_user = UserFactory.create(password=self.password)
        self.admin_user = AdminFactory.create(password=self.password)
        self.expert_user = ExpertFactory.create(password=self.password)
        self.region = RegionFactory.create(with_expert=False)

    def login(self, phone_number, password=None):
        password = password if password is not None else self.password
        data = {"phone_number": phone_number, "password": password}
        res = self.client.post(LOGIN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK, f"{res.data}\ncredential => {data}")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data['access'])
        return self

    def test_add_expert_to_region(self):
        """ Test that with sending the expert_id and region_id, expert is connect to the region """
        self.login(self.admin_user.phone_number)
        with self.assertNumQueries(5):
            """
                1- Retrieve Admin
                2- Retrieve Region
                3- Retrieve Expert(Check existence)
                4- Update Region
                5- Create Note
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": self.region.id})
            data = {"expert_id": self.expert_user.id}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        self.region.refresh_from_db()
        self.assertEqual(self.region.expert_id, self.expert_user.id)

    def test_delete_expert_from_region(self):
        """ Test that sending None as expert_id to endpoint, expert will disconnect from region """
        self.login(self.admin_user.phone_number)
        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Retrieve Region
                3- Update Region
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": self.region.id})
            data = {"expert_id": 0}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        self.region.refresh_from_db()
        self.assertEqual(self.region.expert_id, None)

    def test_update_expert_without_admin(self):
        self.login(self.regular_user.phone_number)
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": self.region.id})
            data = {"expert_id": self.expert_user.id}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        self.region.refresh_from_db()
        self.assertEqual(self.region.expert_id, None)

    def test_list_user_regions_by_admin(self):
        """ Test that admin user(superuser) doesnt have access to this endpoint """
        self.login(self.admin_user.phone_number)

        with self.assertNumQueries(1):
            """
                1- Retrieve user
            """
            res = self.client.get(LIST_REGIONS_USER_URL)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_list_expert_regions_by_admin(self):
        """ Test that admin user(superuser) doesnt have access to this endpoint """
        self.login(self.admin_user.phone_number)

        with self.assertNumQueries(1):
            """
                1- Retrieve user
            """
            res = self.client.get(LIST_REGIONS_EXPERT_URL)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_list_region_by_expert(self):
        RegionFactory.create_batch(10, expert_id=self.expert_user.id)
        self.login(self.expert_user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve expert
                2- Retrieve -> (region, user)
            """
            res = self.client.get(LIST_REGIONS_EXPERT_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertIn("regions", res.data)

        region_count = Region.objects.filter(expert_id=self.expert_user.id).count()
        self.assertEqual(len(res.data["regions"]), region_count)

    def test_list_region_by_user(self):
        RegionFactory.create_batch(10, with_expert=True, user_id=self.regular_user.id)
        self.login(self.regular_user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve regular_user
                2- Retrieve -> (region, expert)
            """
            res = self.client.get(LIST_REGIONS_USER_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        region_count = Region.objects.filter(user_id=self.regular_user.id).count()
        self.assertEqual(len(res.data), region_count)
