from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import ExpertFactory, UserFactory

LOGIN_URL = reverse('users:token_obtain_pair')
REFRESH_URL = reverse('users:token_refresh')


class JWTTestCase(APITestCase):
    def setUp(self) -> None:
        self.user_password = "strongPassword"
        self.user = UserFactory.create(password=self.user_password)
        self.expert_user = ExpertFactory.create(password=self.user_password)

    def test_login(self):
        data = {"phone_number": self.user.phone_number, "password": self.user_password}
        with self.assertNumQueries(1):
            """
                1- Retrieve user
            """
            res = self.client.post(LOGIN_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertIn('refresh', res.data)
            self.assertIn('access', res.data)

    def test_login_invalid_format_phone_number(self):
        data = {"phone_number": "09032567171", "password": self.user_password}
        with self.assertNumQueries(0):
            res = self.client.post(LOGIN_URL, data=data)

            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED, res.data)
            self.assertIn('phone_number', res.data)

    def test_logged_in_user(self):
        data = {"phone_number": self.user.phone_number, "password": self.user_password}
        old_res = self.client.post(LOGIN_URL, data)
        with self.assertNumQueries(1):
            """
                1- Get user
            """
            res = self.client.post(LOGIN_URL, data)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertIn('refresh', res.data)
            self.assertIn('access', res.data)
            self.assertNotEqual(res.data['refresh'], old_res.data['refresh'])
            self.assertNotEqual(res.data['access'], old_res.data['access'])

    def test_refresh(self):
        data = {"phone_number": self.user.phone_number, "password": self.user_password}
        login_res = self.client.post(LOGIN_URL, data)
        with self.assertNumQueries(0):
            res = self.client.post(REFRESH_URL, data={'refresh': login_res.data['refresh']})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)

    def test_refresh_invalid(self):
        with self.assertNumQueries(0):
            res = self.client.post(REFRESH_URL, data={'refresh': 'invalid refresh'})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
