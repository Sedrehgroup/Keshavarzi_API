from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import AdminFactory, UserFactory

CREATE_URL = reverse("users:create")
LOGIN_URL = reverse('users:token_obtain_pair')


def RU_URL(user_id):
    """ Retrieve User URL """
    return reverse("users:retrieve", kwargs={"pk": user_id})


class RegisterUser(APITestCase):
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


class RetrieveUser(APITestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword"
        self.user = UserFactory.create(password=self.password)

    def login(self, phone_number, password=None):
        password = password if password is not None else self.password
        data = {"phone_number": phone_number, "password": password}
        res = self.client.post(LOGIN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK, f"{res.data}\ncredential => {data}")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data['access'])
        return self

    def retrieve_user_by_user_itself(self):
        self.login(self.user.phone_number)
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            res = self.client.get(RU_URL(self.user.id))

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def retrieve_user_by_no_authenticated_user(self):
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            res = self.client.get(RU_URL(self.user.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def retrieve_user_by_admin(self):
        admin = AdminFactory.create(password=self.password)
        self.login(admin.phone_number)
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            res = self.client.get(RU_URL(self.user.id))

            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def retrieve_user_by_another_user(self):
        user2 = UserFactory.create(password=self.password)
        self.login(user2.phone_number)
        with self.assertNumQueries(1):
            """
                1- Retrieve User
            """
            res = self.client.get(RU_URL(self.user.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
