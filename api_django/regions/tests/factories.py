import factory
import factory.fuzzy

from random import randint
from django.contrib.gis.geos import Polygon, MultiPolygon

from regions.models import Region
from users.tests.factories import ExpertFactory, UserFactory


class FuzzyPolygon(factory.fuzzy.BaseFuzzyAttribute):
    """Yields random polygon"""

    def __init__(self, length=None, **kwargs):
        if length is None:
            length = randint(3, 20)
        if length < 3:
            raise Exception("Polygon needs to be 3 or greater in length.")
        self.length = length
        super().__init__(**kwargs)

    def get_random_coords(self):
        latitude = 87.1234 + randint(3, 20)
        longitude = -100.12342 + randint(3, 20)
        return latitude, longitude

    def fuzz(self):
        prefix = suffix = self.get_random_coords()
        coords = [self.get_random_coords() for __ in range(self.length - 1)]
        return Polygon([prefix] + coords + [suffix])


class FuzzyMultiPolygon(factory.fuzzy.BaseFuzzyAttribute):
    """Yields random multipolygon"""

    def __init__(self, length=None, **kwargs):
        if length is None:
            length = randint(2, 20)
        if length < 2:
            raise Exception("MultiPolygon needs to be 2 or greater in length.")
        self.length = length
        super().__init__(**kwargs)

    def fuzz(self):
        polygons = [FuzzyPolygon().fuzz() for __ in range(self.length)]
        return MultiPolygon(*polygons)


class RegionFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("pyint", min_value=0)
    name = factory.Faker("name")
    user = factory.SubFactory(UserFactory, phone_number="+989032567184")
    polygon = FuzzyPolygon()

    @classmethod
    def create(cls, with_expert=False, **kwargs):
        if with_expert:
            expert = ExpertFactory.create()
            return super(RegionFactory, cls).create(**kwargs, expert=expert)
        return super(RegionFactory, cls).create(**kwargs)

    class Meta:
        model = Region
