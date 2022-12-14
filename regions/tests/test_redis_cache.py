from unittest import TestCase

from django.core.cache import cache

from regions.tools.cache_tools import get_weather_forcast


class TestRedisCache(TestCase):
    def test_get_weather_forcast_function_is_set_cache_correctly(self):
        region_id = 1
        lat = "40.75872069597532"
        lon = "-73.98529171943665"

        self.assertIsNone(cache.get(str(region_id)))
        forcast = get_weather_forcast(region_id, lat, lon)
        self.assertIsNotNone(forcast)
        self.assertIsNotNone(cache.get(region_id))
        self.assertEqual(cache.get(str(region_id)), forcast)

        cache.delete(region_id)
