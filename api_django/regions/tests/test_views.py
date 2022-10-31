import os

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config.settings import BASE_DIR
from regions.models import Region
from regions.tests.factories import RegionFactory, fake_polygon_geojson
from regions.utils import get_polygon_by_geojson
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")
LIST_REGIONS_EXPERT_URL = reverse("regions:list_expert_regions")
LIST_REGIONS_USER_URL = reverse("regions:list_user_regions")
CREATE_REGION_URL = reverse("regions:create")
TEST_TIF = os.path.join(BASE_DIR, "regions", "tests", "tif_test.tif")


class RegionViewsTestCase(APITestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword123#@!"
        self.user = UserFactory.create(password=self.password)
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

    def test_attach_expert_to_region_with_admin(self):
        self.login(self.admin_user.phone_number)
        with self.assertNumQueries(5):
            """
                1- Retrieve User
                2- Retrieve Region
                3- Check expert
                4- Update Region
                5- Create Note
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": self.region.id})
            data = {"expert_id": self.expert_user.id}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertEqual(res.data, {"expert_id": self.expert_user.id})

        self.region.refresh_from_db()
        self.assertIsNotNone(self.region.expert_id)

    def test_attach_expert_to_region_with_user(self):
        self.login(self.user.phone_number)
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

    def test_detach_expert_from_region_with_admin(self):
        self.login(self.admin_user.phone_number)
        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Retrieve Region
                3- Update Region
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": self.region.id})
            data = {"expert_id": ""}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertEqual(res.data, {"expert_id": None})

        self.region.refresh_from_db()
        self.assertIsNone(self.region.expert_id)

    def test_detach_expert_from_region_by_expert(self):
        """ Test that expert can not detach himself from region """
        region = RegionFactory.create(with_expert=True)
        region_expert_id = region.expert_id
        self.login(self.expert_user.phone_number)
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            url = reverse("regions:update_region_expert", kwargs={"pk": region.id})
            data = {"expert_id": ""}
            res = self.client.put(url, data)
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        self.region.refresh_from_db()
        self.assertEqual(region.expert_id, region_expert_id)

    def test_list_user_regions_by_admin(self):
        """ Test that admin user(superuser) doesnt have access to this endpoint """
        self.login(self.admin_user.phone_number)
        self.region.expert_id = self.expert_user.id
        self.region.save(update_fields=['expert_id'])

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
                2- Retrieve -> region
            """
            res = self.client.get(LIST_REGIONS_EXPERT_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        region_count = Region.objects.filter(expert_id=self.expert_user.id).count()
        self.assertEqual(len(res.data), region_count)
        try:
            for region in res.data:
                get_polygon_by_geojson(region["polygon"])
        except Exception as e:
            self.fail({"convert geojson to polygon": e})

    def test_list_region_by_user(self):
        RegionFactory.create_batch(10, with_expert=True, user_id=self.user.id)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve user
                2- Retrieve -> (region, expert)
            """
            res = self.client.get(LIST_REGIONS_USER_URL)
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        region_count = Region.objects.filter(user_id=self.user.id).count()
        self.assertEqual(len(res.data), region_count)
        try:
            for region in res.data:
                get_polygon_by_geojson(region["polygon"])
        except Exception as e:
            self.fail({"convert geojson to polygon": e})

    def test_create_new_region_with_user(self):
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Check existence of user
                2- Create region
            """
            data = {"name": "test_name", "polygon": fake_polygon_geojson}
            res = self.client.post(CREATE_REGION_URL, data, format="json")
            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        qs = Region.objects.filter(user_id=self.user.id)
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, data["name"])

    def test_create_new_region_with_expert(self):
        """ Test that expert user can not create region """
        self.login(self.expert_user.phone_number)
        with self.assertNumQueries(1):
            """
                0- Without query
            """
            data = {"name": "test_name", "polygon": fake_polygon_geojson}
            res = self.client.post(CREATE_REGION_URL, data, format="json")
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        qs = Region.objects.filter(user_id=self.expert_user.id)
        self.assertEqual(qs.count(), 0)

    def test_create_new_region_with_admin(self):
        """ Test that admin user can not create region """
        self.login(self.admin_user.phone_number)
        with self.assertNumQueries(1):
            """
                0- Without query
            """
            data = {"name": "test_name", "polygon": fake_polygon_geojson}
            res = self.client.post(CREATE_REGION_URL, data, format="json")
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

        qs = Region.objects.filter(user_id=self.expert_user.id)
        self.assertEqual(qs.count(), 0)

    def test_create_new_region_with_invalid_geojson(self):
        """ Test that sending geojson without coordinates is raising BadRequest exception """
        without_coord = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "coordinates": [[]],
                        "type": "Polygon"
                    }
                }
            ]
        }
        self.login(self.user.phone_number)
        with self.assertNumQueries(1):
            """
                1- Without query
            """
            data = {"name": "test_name", "polygon": without_coord}
            res = self.client.post(CREATE_REGION_URL, data, format="json")
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, res.data)

        qs = Region.objects.filter(user_id=self.user.id)
        self.assertEqual(qs.count(), 0)
