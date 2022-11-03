from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from notes.models import Note
from regions.models import Region
from regions.tests.factories import RegionFactory, fake_polygon
from users.tests.factories import ExpertFactory, UserFactory


class RegionModelTestCase(APITestCase):
    def test_factory_create_region_with_expert(self):
        region = RegionFactory.create(with_expert=True)

        self.assertIsNotNone(region.user_id)
        self.assertIsNotNone(region.expert_id)

    def test_create_region(self):
        user = UserFactory.create()

        region = Region.objects.create(user_id=user.id, polygon=fake_polygon, name="test polygon")

        self.assertTrue(region.is_active)
        self.assertEqual(region.polygon, fake_polygon)
        self.assertEqual(region.user_id, user.id)
        self.assertIsNone(region.expert_id)
        self.assertIsNone(region.dates)

    def test_add_expert_will_create_note(self):
        """ Test that after adding expert to region, a note is created. """
        region = RegionFactory.create(with_expert=False)
        expert = ExpertFactory.create()

        region.expert_id = expert.id
        region.save(update_fields=["expert_id"])

        note = Note.objects.filter(region=region, user=expert)
        self.assertEqual(note.count(), 1)
        self.assertIsNotNone(note.first().text)

    def test_detach_expert_with_none_value_will_not_create_note(self):
        """ Test that set 'None' to expert_id of region, will not create note. """
        region = RegionFactory.create(with_expert=True)
        self.assertIsNotNone(region.expert_id)

        region.expert_id = None
        region.save(update_fields=["expert_id"])
        self.assertIsNone(region.expert_id)

        note = Note.objects.filter(region_id=region.id)
        self.assertEqual(note.count(), 0)

    def test_detach_expert_with_0_value_is_not_working(self):
        """ Test that set '0' to expert_id of region, will not create note. """
        region = RegionFactory.create(with_expert=True)
        self.assertIsNotNone(region.expert_id)

        with self.assertRaises(ValidationError):
            region.expert_id = 0
            region.save(update_fields=["expert_id"])

        self.assertTrue(region.expert_id in (0, None))  # Is not 0 or None
        self.assertEqual(Note.objects.filter(region_id=region.id).count(), 0)
