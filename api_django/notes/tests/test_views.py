import os

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config.settings import BASE_DIR
from notes.models import Note
from regions.models import Region
from regions.tests.factories import RegionFactory
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")
CREATE_NOTE_URL = reverse("notes:create")
TEST_TIF = os.path.join(BASE_DIR, "regions", "tests", "tif_test.tif")


class BaseNotesTestCase(APITestCase):
    def setUp(self) -> None:
        self.password = "VeryStrongPassword123#@!"
        self.user = UserFactory.create(password=self.password)
        self.expert = ExpertFactory.create(password=self.password)
        self.admin = AdminFactory.create(password=self.password)
        self.region = RegionFactory.create()

    def login(self, phone_number, password=None):
        password = password if password is not None else self.password
        data = {"phone_number": phone_number, "password": password}
        res = self.client.post(LOGIN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK, f"{res.data}\ncredential => {data}")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.data['access'])
        return self


class CreateNoteTestCase(BaseNotesTestCase):
    def test_create_note_with_invalid_region_id(self):
        """ Test that posting not existing region_id, will return 404 response """
        self.login(self.user.phone_number)
        text = "<< test_create_note_with_invalid_region_id >> Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        max_region_id = Region.objects.order_by("id").only("id").last().id

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Check existence of region
            """
            data = {"text": text, "region_id": max_region_id + 1}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, res.data)

    def test_create_note_as_user(self):
        self.login(self.user.phone_number)
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of region
                3- Insert Note
            """
            data = {"text": text, "region_id": self.region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        note = Note.objects.filter(region_id=self.region.id)
        self.assertEqual(note.count(), 1)
        self.assertEqual(note.first().user_role, "U")

    def test_create_note_as_expert(self):
        self.login(self.expert.phone_number)
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of region
                3- Insert Note
            """
            data = {"text": text, "region_id": self.region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        note_by_region = Note.objects.filter(region_id=self.region.id)
        note_by_expert = Note.objects.filter(user_id=self.expert.id)
        self.assertEqual(note_by_region.count(), 1)
        self.assertEqual(note_by_expert.count(), 1)
        self.assertEqual(note_by_expert.first(), note_by_region.first())
        self.assertEqual(note_by_region.first().user_role, "E")

    def test_create_note_as_admin(self):
        self.login(self.admin.phone_number)
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of region
                3- Insert Note
            """
            data = {"text": text, "region_id": self.region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)

        note = Note.objects.filter(region_id=self.region.id)
        self.assertEqual(note.count(), 1)
        self.assertEqual(note.first().user_role, "A")


class UpdateNoteTestCase(BaseNotesTestCase):
    def test_update_note_as_user(self):
        pass