from rest_framework.test import APITestCase

from notes.models import Note
from regions.models import Region
from regions.tests.factories import RegionFactory, FuzzyPolygon
from users.tests.factories import ExpertFactory, UserFactory


class RegionModelTestCase(APITestCase):
    def test_factory_create_region_with_expert(self):
        region = RegionFactory.create(with_expert=True)

        self.assertIsNotNone(region.user_id)
        self.assertIsNotNone(region.expert_id)

    def test_create_region(self):
        user = UserFactory.create()
        pl = FuzzyPolygon().fuzz()

        region = Region.objects.create(user_id=user.id, polygon=pl, name="test polygon")

        self.assertTrue(region.is_active)
        self.assertEqual(region.polygon, pl)
        self.assertEqual(region.user_id, user.id)
        self.assertIsNone(region.expert_id)
        self.assertIsNone(region.dates)

    def test_add_expert_will_create_note(self):
        """ Test that after adding expert to region, a note is created. """
        region = RegionFactory.create(with_expert=False)
        expert = ExpertFactory.create()

        region.expert_id = expert.id
        region.save(update_fields=["expert_id"])

        note = Note.objects.filter(region=region, expert=expert)
        self.assertEqual(note.count(), 1)
        self.assertIsNotNone(note.first().text)
