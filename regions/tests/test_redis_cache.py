from unittest import TestCase

from django.core.cache import cache

from regions.tools.cache_tools import get_weather_forcast


class TestRedisCache(TestCase):
    def test_get_weather_forcast_function_is_set_cache_correctly(self):
        key = "test_key"
        lat = "40.75872069597532"
        lon = "-73.98529171943665"

        self.assertIsNone(cache.get(key))
        forcast = get_weather_forcast(key, lat, lon)
        self.assertIsNotNone(forcast)
        self.assertIsNotNone(cache.get(key))
        self.assertEqual(cache.get(key), forcast)

        cache.delete(key)
