import os

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from config.settings import BASE_DIR
from notes.models import Note
from notes.tests.factories import NoteFactory
from regions.models import Region
from regions.tests.factories import RegionFactory
from users.tests.factories import AdminFactory, ExpertFactory, UserFactory

LOGIN_URL = reverse("users:token_obtain_pair")
CREATE_NOTE_URL = reverse("notes:list_create")
LIST_USER_NOTES_URL = reverse("notes:list_create")
TEST_TIF = os.path.join(BASE_DIR, "regions", "tests", "tif_test.tif")


def RUD_URL(note_id):
    """ Retrieve Update Destroy URL """
    return reverse("notes:retrieve_update_destroy", kwargs={"pk": note_id})


def LNBR_URL(region_id):
    """ List Notes By Region URL """
    return reverse("notes:list_notes_by_region", kwargs={"pk": region_id})


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


class ListNoteTestCase(BaseNotesTestCase):
    def test_creator_can_list_own_notes(self):
        notes = NoteFactory.create_batch(user=self.user, size=15)
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Notes
            """
            res = self.client.get(LIST_USER_NOTES_URL)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_only_creator_can_list_own_notes(self):
        NoteFactory.create(user=self.user)
        self.login(self.expert.phone_number)

        Note.objects.filter(user_id=self.expert.id).delete()
        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Notes
            """
            res = self.client.get(LIST_USER_NOTES_URL)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
            self.assertEqual(len(res.data), 0)


class ListNoteByRegionTestCase(BaseNotesTestCase):
    def test_result_schema(self):
        region = RegionFactory.create(user=self.user)
        NoteFactory.create_batch(user=region.user, region=region, size=12)

        self.login(self.user.phone_number)
        res = self.client.get(LNBR_URL(region.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

        self.assertIn("count", res.data)
        self.assertIn("next", res.data)
        self.assertIn("previous", res.data)
        self.assertIn("results", res.data)

        self.assertEqual(len(res.data["results"]), 10)

        self.assertIn("id", res.data["results"][0])
        self.assertIn("user", res.data["results"][0])
        self.assertIn("user_role", res.data["results"][0])
        self.assertIn("text", res.data["results"][0])
        self.assertIn("created_date", res.data["results"][0])
        self.assertIn("updated_date", res.data["results"][0])

        self.assertTrue(res.data["results"][0]["user_role"] == "U", res.data["results"][0]["user_role"])
        self.assertIsNone(res.data["results"][0]["updated_date"])

    def test_user_can_get_notes_list(self):
        region = RegionFactory.create(user=self.user)
        NoteFactory.create_batch(region=region, user=self.user, size=20)
        self.login(self.user.phone_number)

        with self.assertNumQueries(4):
            """
                1- Retrieve User
                2- Retrieve Region
                3- Count the number of notes(Pagination)
                4- Retrieve Note
            """
            res = self.client.get(LNBR_URL(region.id))

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertEqual(res.data["count"], 20)
        self.assertEqual(len(res.data["results"]), 10)

    def test_expert_can_get_notes_list(self):
        region = RegionFactory.create(user=self.expert)
        NoteFactory.create_batch(user=self.expert, region=region, size=15)
        self.login(self.expert.phone_number)

        with self.assertNumQueries(4):
            """
                1- Retrieve User
                2- Retrieve Region
                3- Count the number of notes(Pagination)
                3- Retrieve Note
            """
            res = self.client.get(LNBR_URL(region.id))

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertEqual(res.data["count"], 15)
        self.assertEqual(len(res.data["results"]), 10)

    def test_admin_can_get_notes_list(self):
        region = RegionFactory.create()
        NoteFactory.create_batch(user=region.user, region=region, size=12)
        # ** -> Admin is not note creator or user/expert of region
        self.login(self.admin.phone_number)

        with self.assertNumQueries(4):
            """
                1- Retrieve User
                2- Retrieve Region
                2- Count the number of notes(Pagination)
                3- Retrieve Note
            """
            res = self.client.get(LNBR_URL(region.id))

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)
        self.assertEqual(res.data["count"], 12)
        self.assertEqual(len(res.data["results"]), 10)

    def test_user_without_relation_to_region_can_not_get_notes_list(self):
        user1, user2 = UserFactory.create(password=self.password), UserFactory.create(password=self.password)
        region = RegionFactory.create(user=user1)
        NoteFactory.create_batch(user=region.user, region=region, size=11)
        self.login(user2.phone_number)  # Login the second user. Not the notes creator.

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(LNBR_URL(region.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_expert_without_relation_to_region_can_not_get_notes_list(self):
        expert1, expert2 = ExpertFactory.create(password=self.password), ExpertFactory.create(password=self.password)
        region = RegionFactory.create(user=expert1)
        NoteFactory.create_batch(user=expert1, region=region, size=11)
        self.login(expert2.phone_number)  # Login the second expert. Note the notes creator

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Region
            """
            res = self.client.get(LNBR_URL(region.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)

    def test_list_notes_with_not_exists_region(self):
        invalid_region_id = Region.objects.order_by("id").only("id").last().id + 1
        self.login(self.user.phone_number)

        with self.assertNumQueries(2):
            """ 
                1- Retrieve User
                2- Count Notes
            """
            res = self.client.get(LNBR_URL(invalid_region_id))

            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, res.data)


class CreateNoteTestCase(BaseNotesTestCase):
    def create_and_test_region(self, user):
        region = RegionFactory.create(user_id=user.id)
        self.login(user.phone_number)
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check existence of region
                3- Insert Note
            """
            data = {"text": text, "region_id": region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        return region

    def test_create_note_with_invalid_region_id(self):
        """ Test that posting not existing region_id, will return 404 response """
        self.login(self.user.phone_number)
        text = "<< test_create_note_with_invalid_region_id >> Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        max_region_id = Region.objects.order_by("id").only("id").last().id

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check relation of user or expert to region
                3- Check existence of region
            """
            data = {"text": text, "region_id": max_region_id + 1}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND, res.data)

    def test_create_note_as_user(self):
        region = self.create_and_test_region(self.user)

        note = Note.objects.filter(region_id=region.id)
        self.assertEqual(note.count(), 1)
        self.assertEqual(note.first().user_role, "U")

    def test_create_note_as_expert(self):
        region = self.create_and_test_region(self.expert)

        note_by_region = Note.objects.filter(region_id=region.id)
        note_by_expert = Note.objects.filter(user_id=self.expert.id)
        self.assertEqual(note_by_region.count(), 1)
        self.assertEqual(note_by_expert.count(), 1)
        self.assertEqual(note_by_expert.first(), note_by_region.first())
        self.assertEqual(note_by_region.first().user_role, "E")

    def test_create_note_as_admin_with_matching_region(self):
        region = self.create_and_test_region(self.admin)

        note = Note.objects.filter(region_id=region.id)
        self.assertEqual(note.count(), 1)
        self.assertEqual(note.first().user_role, "A")

    def test_create_note_as_admin_without_matching_region(self):
        region = RegionFactory.create()
        self.assertNotEqual(region.user, self.admin)
        self.login(self.admin.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check relation of user or expert to region
                3- Check existence of region
            """
            data = {"text": " I am admin. I am allowed to do whatever I want", "region_id": region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_note_without_user_or_expert(self):
        """ Test that if user is not region.user or region.expert, validation error is raising """
        region = RegionFactory.create()
        self.assertNotEqual(region.user, self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Check relation of user or expert to region
                3- Check existence of region
            """
            data = {"text": "This test should fail", "region_id": region.id}
            res = self.client.post(CREATE_NOTE_URL, data)

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, res.data)


class UpdateNoteTestCase(BaseNotesTestCase):
    def base_test_update_as(self, user, user_role):
        self.login(user.phone_number)
        note = NoteFactory.create(user_id=user.id, user_role=user_role)

        with self.assertNumQueries(3):
            """
                1- Retrieve user
                2- Retrieve object
                3- Update object
            """
            data = {"text": "new_text"}
            res = self.client.patch(RUD_URL(note.id), data)

            self.assertEqual(res.status_code, status.HTTP_200_OK, res.data)

    def test_update_note_as_user(self):
        self.base_test_update_as(self.user, "U")

    def test_update_note_as_admin(self):
        self.base_test_update_as(self.admin, "A")

    def test_update_note_as_expert(self):
        self.base_test_update_as(self.expert, "E")

    def test_that_only_creator_can_edit_note(self):
        note = NoteFactory.create(user_id=ExpertFactory.create().id)
        self.login(self.expert.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Note
            """
            data = {"text": "This test should fail"}
            res = self.client.patch(RUD_URL(note.id), data)

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN, res.data)


class DeleteNoteTestCase(BaseNotesTestCase):
    def test_delete_note_by_creator(self):
        note = NoteFactory.create(user=self.user)
        self.login(self.user.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Retrieve Note
                3- Delete Note
            """
            res = self.client.delete(RUD_URL(note.id))

            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT, res.data)

    def test_delete_users_note_by_admin(self):
        note = NoteFactory.create()
        self.login(self.admin.phone_number)

        with self.assertNumQueries(3):
            """
                1- Retrieve User
                2- Retrieve Note
                3- Delete Note
            """
            res = self.client.delete(RUD_URL(note.id))

            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT, res.data)

    def test_delete_user1s_note_by_user2(self):
        user1, user2 = tuple(UserFactory.create_batch(password=self.password, size=2))
        note = NoteFactory.create(user_id=user1.id)
        self.login(user2.phone_number)

        with self.assertNumQueries(2):
            """
                1- Retrieve User
                2- Retrieve Note
            """
            res = self.client.delete(RUD_URL(note.id))

            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
