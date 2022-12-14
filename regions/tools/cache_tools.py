from datetime import timedelta

import requests

from os import environ
from django.core.cache import cache
from jdatetime import datetime

API_KEY = environ["TOMORROW_API_KEY"]

def get_weather_forcast(region_id, lat, lon, start_time="now", end_time="nowPlus14d", time_steps="1d"):
    cached_weather = cache.get(region_id)
    if cached_weather:
        return cached_weather
    url = "https://api.tomorrow.io/v4/timelines"
    api_key = API_KEY
    params = {
        "apikey": api_key,
        "fields": "humidity,temperatureMin,temperatureMax",  # Without any space
        "location": f"{lat},{lon}",
        "timesteps": time_steps,
        "startTime": start_time,
        "endTime": end_time,
        "units": "metric"
    }
    response = requests.get(url, params, headers={"Content-Type": "application/json"})
    if response.status_code != 200:
        if response.status_code == 403:
            print("API key is not valid any more. change it.")
            return response.content
        print(response.status_code)
        print(response.content)
        return
    forcast = response.content
    now = datetime.now()
    midnight = now.replace(hour=23, minute=59, second=59)
    time_until_end_of_day = (midnight - now).seconds
    cache.set(key=region_id, value=forcast, timeout=time_until_end_of_day)
    return response.content
