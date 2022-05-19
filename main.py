import sys
import datetime
from dotenv import load_dotenv
from openweathermap import get_forecast_per_city_per_hour, get_current_feels_like

load_dotenv()

UNIX_DAY=60*60*24


class City:
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon


CITIES = [
    City('Jerusalem', '31.7788242', '35.2257626'),
    City('Haifa', '32.8191218', '34.9983856'),
    City('TelAviv', '32.0852997', '34.7818064'),
    City('Eilat', '29.5569348', '34.9497949'),
    City('Tiberias', '32.7892439', '35.5213860')
]


def slice_hourly_by_days(hourly_forecast):
    result = {}
    today_morning = int(datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%s'))
    for measurement in hourly_forecast:
        diff_since_morning = measurement['dt'] - today_morning
        day_index = int(diff_since_morning / UNIX_DAY)
        if result.get(str(day_index)) is None:
            result[str(day_index)] = []
        result[str(day_index)].append(measurement)

    return result


def get_avg_tmp_per_day(city):
    hourly_forecast = get_forecast_per_city_per_hour(city)
    sliced_hourly_forecast = slice_hourly_by_days(hourly_forecast)
    result = {
        'name': city.name,
        'avg_per_day': {}
    }
    for day_index in sliced_hourly_forecast:
        sum_temp = sum(c['temp'] for c in sliced_hourly_forecast[day_index])
        sum_days = len(sliced_hourly_forecast[day_index])
        result['avg_per_day'][day_index] = sum_temp / sum_days

    return result


def get_avg_tmp_per_city_per_day(request):
    result = []
    for city in CITIES:
        result.append(get_avg_tmp_per_day(city))

    return {'data': result}


def get_lowest_humid(request):
    lowest_humidity = {
        'city': 'NA',
        'time': 'NA',
        'humidity': sys.maxsize,
    }
    for city in CITIES:
        hourly_forecast = get_forecast_per_city_per_hour(city)
        min_in_city = min(hourly_forecast, key=lambda x: x['humidity'])
        if min_in_city['humidity'] < lowest_humidity['humidity']:
            lowest_humidity = {
                'city': city.name,
                'time': min_in_city['dt'],
                'humidity': min_in_city['humidity'],
            }

    return {'data': lowest_humidity}


def get_feels_like_rank(request):
    order = request.args.get('order')
    result = []
    for city in CITIES:
        result.append({
            'name': city.name,
            'feels_like': get_current_feels_like(city)
        })

    result.sort(key=lambda x: x['feels_like'], reverse=(order == 'desc'))
    return {'data': result}
