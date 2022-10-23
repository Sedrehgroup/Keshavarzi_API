from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory

CREATE_URL = reverse("users:create")


class UsersViewsTestCase(APITestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword"
        self.user = UserFactory.create(password=self.password)

    def test_register(self):
        data = {"phone_number": "+989032567185", "password": self.password}
        with self.assertNumQueries(2):
            """
                1- Check if user with that username exists
                2- Create new user with given credential
            """
            res = self.client.post(CREATE_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
            self.assertIn('access', res.data)
            self.assertIn('refresh', res.data)

    def test_register_short_phone_number(self):
        data = {"phone_number": "+98903256718", "password": "StrongPassword"}
        with self.assertNumQueries(1):
            """
                1- Check user exists or not
            """
            res = self.client.post(CREATE_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("phone_number", res.data)

    def test_register_long_phone_number(self):
        data = {"phone_number": "+9890325671811", "password": "StrongPassword"}
        with self.assertNumQueries(1):
            """
                1- Check existence of user
            """
            res = self.client.post(CREATE_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('phone_number', res.data)

    def test_register_invalid_format(self):
        data = {"phone_number": "09032567181", "password": "StrongPassword"}
        with self.assertNumQueries(1):
            """
                1- Check phone_number is exists
            """
            res = self.client.post(CREATE_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('phone_number', res.data)

    def test_register_duplicated_username_field(self):
        """ Check if user with that username is already exists """
        data = {"phone_number": self.user.phone_number, "password": self.password}
        with self.assertNumQueries(1):
            res = self.client.post(CREATE_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('phone_number', res.data)
