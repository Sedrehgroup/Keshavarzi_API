import factory.fuzzy

from regions.models import Region
from regions.utils import get_polygon_by_geojson
from users.tests.factories import ExpertFactory, UserFactory

# class FuzzyPolygon(factory.fuzzy.BaseFuzzyAttribute):
#     """Yields random polygon"""
#
#     def __init__(self, length=None, **kwargs):
#         if length is None:
#             length = randint(3, 20)
#         if length < 3:
#             raise Exception("Polygon needs to be 3 or greater in length.")
#         self.length = length
#         super().__init__(**kwargs)
#
#     def get_random_coords(self):
#         latitude = 87.1234 + randint(3, 20)
#         longitude = -100.12342 + randint(3, 20)
#         return latitude, longitude
#
#     def fuzz(self):
#         prefix = suffix = self.get_random_coords()
#         coords = [self.get_random_coords() for __ in range(self.length - 1)]
#         return Polygon([prefix] + coords + [suffix])
#
#     def fuzz_geom(self, convert_json=False):
#         pl = self.fuzz()
#         return get_geojson_by_polygon(pl, convert_json=convert_json)
#
#
# class FuzzyMultiPolygon(factory.fuzzy.BaseFuzzyAttribute):
#     """Yields random multipolygon"""
#
#     def __init__(self, length=None, **kwargs):
#         if length is None:
#             length = randint(2, 20)
#         if length < 2:
#             raise Exception("MultiPolygon needs to be 2 or greater in length.")
#         self.length = length
#         super().__init__(**kwargs)
#
#     def fuzz(self):
#         polygons = [FuzzyPolygon().fuzz() for __ in range(self.length)]
#         return MultiPolygon(*polygons)

fake_polygon_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [51.409403559714630, 35.711869581133980],
                        [51.380123630530960, 35.699606764465290],
                        [51.402193118009590, 35.681678195995330],
                        [51.428987994663544, 35.69355360445098],
                        [51.425025758274930, 35.713942498675820],
                        [51.415102069174340, 35.718267020243530],
                        [51.406425611124064, 35.71949939177594],
                        [51.409403559714630, 35.711869581133980]
                    ]
                ]
            }
        }
    ]
}
fake_polygon_geojson_2 = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [51.415829632319060, 35.813202441237180],
                        [51.415829632319060, 35.779131730655960],
                        [51.484725693615760, 35.786258677906346],
                        [51.479383271521186, 35.813202441237180],
                        [51.415829632319060, 35.813202441237180]
                    ]
                ]
            }
        }
    ]
}
fake_polygon = get_polygon_by_geojson(fake_polygon_geojson)


class RegionFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("pystr", max_chars=20)
    user = factory.SubFactory(UserFactory)
    polygon = fake_polygon

    @classmethod
    def create(cls, with_expert=False, **kwargs):
        if with_expert:
            expert = ExpertFactory.create()
            return super(RegionFactory, cls).create(**kwargs, expert=expert)
        return super(RegionFactory, cls).create(**kwargs)

    class Meta:
        model = Region
