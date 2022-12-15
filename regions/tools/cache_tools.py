import logging
import requests

from os import environ, getenv
from django.core.cache import cache
from datetime import datetime

TOMORROW_REQUEST_TIMEOUT = int(getenv("TOMORROW_REQUEST_TIMEOUT", 2))
TOMORROW_REQUEST_URL = "https://api.tomorrow.io/v4/timelines"
TOMORROW_MAXIMUM_RESET_CACHE_PER_DAY = int(getenv("TOMORROW_MAXIMUM_RESET_CACHE_PER_DAY", 20))
logger = logging.getLogger("cache_tools")  # ToDo: Config the logger


def get_today_str_time():
    logger.debug("get today str time")
    return datetime.today().strftime("%Y-%M-%d")


def get_seconds_until_end_of_day():
    logger.debug("get seconds until end of day ")
    now = datetime.now()
    midnight = now.replace(hour=23, minute=59, second=59)
    return (midnight - now).seconds


def initialize_keys_and_index(reset_count=0, today_str_time=None):
    logger.debug("initialize keys and index")
    keys = str(environ.get("TOMORROW_API_KEY")).split()
    index = len(keys)
    value = {"reset_count": reset_count,
             "keys": keys, "index": index,
             "time_last_initialize": today_str_time or get_today_str_time()}
    logger.debug("initialized value: ")
    logger.debug(value)
    cache.set("keys_and_index", value)
    return keys, index


def reset_api_keys(keys_and_index):
    logger.debug("reset api keys")
    reset_count = keys_and_index["reset_count"]
    today_str_time = get_today_str_time()
    if reset_count == TOMORROW_MAXIMUM_RESET_CACHE_PER_DAY:
        if keys_and_index["time_last_initialize"] == today_str_time:
            # ToDo: Mail to admin
            logger.critical("Maximum limit of tomorrow api is reached")
        return initialize_keys_and_index(0, today_str_time)
    return initialize_keys_and_index(reset_count + 1, today_str_time)


def get_api_key():
    logger.debug("get api key")
    keys_and_index = cache.get("keys_and_index")
    if not keys_and_index:
        logger.debug("keys_and_index is not available")
        keys, index = initialize_keys_and_index()
    else:
        logger.debug("keys_and_index is available")
        keys, index = keys_and_index["keys"], keys_and_index["index"]

        logger.debug(f"keys_and_index[index] = {index}")
        if index == 0:
            reset_api_keys(keys_and_index)
        else:
            keys_and_index.update({"index": index - 1})
        cache.set(key="keys_and_index", value=keys_and_index, timeout=get_seconds_until_end_of_day())

    return keys[index]


def send_request_to_tomorrow(params):
    logger.debug("send_request_to_tomorrow")
    params.update({"apikey": get_api_key()})
    logger.debug("params:")
    logger.debug(params)
    logger.debug("send request")
    try:
        return requests.get(TOMORROW_REQUEST_URL, params,
                            timeout=TOMORROW_REQUEST_TIMEOUT)
    except requests.exceptions.ReadTimeout as e:
        return send_request_to_tomorrow(params)


def get_weather_forcast(key, lat, lon, time_steps="1d",
                        start_time="now", end_time="nowPlus14d"):
    logger.debug("get weather forcast")
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

    cache.set(key, response.content, timeout=get_seconds_until_end_of_day())
    return response.content
