import os
import requests
import redis
import pickle
from dotenv import load_dotenv

load_dotenv()

cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), password=os.getenv('REDIS_PASSWORD'))

CACHE_VERSION=os.getenv('CACHE_VERSION')
GEO_BASE_URL=os.getenv('GEO_BASE_URL')
DATA_ONE_CALL_BASE_URL=os.getenv('DATA_ONE_CALL_BASE_URL')
DATA_WEATHER_BASE_URL=os.getenv('DATA_WEATHER_BASE_URL')
API_ID=os.getenv('API_ID')
CACHE_EXPIRATION=3600


def _get_city_coordinates(_city):
    url = f'{GEO_BASE_URL}q={_city}&limit=1&{API_ID}'
    response = requests.get(url).json()
    response_in_israel = [x for x in response if x['country'] == 'IL'][0]
    return response_in_israel['lat'], response_in_israel['lon']


def get_forecast_per_city_per_hour(city):
    key = f'get_forecast_per_city_per_hour_{city.name}_{CACHE_VERSION}'
    cache_response = cache.get(key)
    if cache_response:
        return pickle.loads(cache_response)['hourly']
    else:
        url = f'{DATA_ONE_CALL_BASE_URL}lat={city.lat}&lon={city.lon}&exclude=current,minutely,daily,alerts&units=metric&{API_ID}'
        response = requests.get(url).json()
        cache.set(key, pickle.dumps(response), ex=CACHE_EXPIRATION)
        return response['hourly']


def get_current_feels_like(city):
    key = f'get_current_feels_like_{city.name}_{CACHE_VERSION}'
    cache_response = cache.get(key)
    if cache_response:
        return pickle.loads(cache_response)['main']['feels_like']
    else:
        url = f'{DATA_WEATHER_BASE_URL}lat={city.lat}&lon={city.lon}&{API_ID}'
        response = requests.get(url).json()
        cache.set(key, pickle.dumps(response), ex=CACHE_EXPIRATION)
        return response['main']['feels_like']
