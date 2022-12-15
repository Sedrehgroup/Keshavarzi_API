import logging
import requests

from os import environ, getenv
from django.core.cache import cache
from datetime import datetime

TOMORROW_REQUEST_TIMEOUT = getenv("TOMORROW_REQUEST_TIMEOUT", 2)
TOMORROW_REQUEST_URL = "https://api.tomorrow.io/v4/timelines"
logger = logging.getLogger("cache_tools")


def initialize_keys_and_index():
    value = {
        "keys": str(environ.get("TOMORROW_API_KEY")),
        "index": 0
    }
    cache.set("keys_and_index", value)
    return value


def get_api_key():
    keys_and_index = cache.get("keys_and_index")
    if not keys_and_index:
        keys_and_index = initialize_keys_and_index()

    keys, index = keys_and_index["keys"], keys_and_index["index"]
    keys_and_index.update({"index": index + 1})

    cache.set(key="keys_and_index", value=keys_and_index)
    return keys[index]


def send_request_to_tomorrow(params):
    params.update({"apikey": get_api_key()})
    try:
        return requests.get(TOMORROW_REQUEST_URL, params,
                            timeout=TOMORROW_REQUEST_TIMEOUT)
    except requests.exceptions.ReadTimeout as e:
        return send_request_to_tomorrow(params)


def get_weather_forcast(key, lat, lon,
                        start_time="now", end_time="nowPlus14d", time_steps="1d"):
    cached_weather = cache.get(key)
    if cached_weather:
        return cached_weather
    params = {
        "fields": "humidity,temperatureMin,temperatureMax",  # Without any space
        "location": f"{lat},{lon}",
        "timesteps": time_steps,
        "startTime": start_time,
        "endTime": end_time,
        "units": "metric"
    }
    response = send_request_to_tomorrow(params)
    if response.status_code != 200:
        logger.critical(response.content)

    now = datetime.now()
    midnight = now.replace(hour=23, minute=59, second=59)
    second_until_end_of_day = (midnight - now).seconds
    cache.set(key, response.content, timeout=second_until_end_of_day)
    return response.content
