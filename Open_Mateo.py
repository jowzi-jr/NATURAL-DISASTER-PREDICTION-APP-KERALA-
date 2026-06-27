import openmeteo_requests
import requests_cache
from retry_requests import retry

# Cache responses for one hour
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "wind_speed_10m",
            "surface_pressure",
            "cloud_cover",
            "visibility",
            "weather_code",
            "precipitation"
        ],
        "daily": ["uv_index_max"], # UV index is usually tracked daily
        "timezone": "Asia/Kolkata"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    current = response.Current()
    daily = response.Daily()

    weather = {
        "temperature": current.Variables(0).Value(),
        "humidity": current.Variables(1).Value(),
        "wind_speed": current.Variables(2).Value(),
        "pressure": current.Variables(3).Value(),
        "cloud_cover_percent": current.Variables(4).Value(),
        "visibility_km": current.Variables(5).Value() / 1000, # Convert meters to km
        "weather_code": current.Variables(6).Value(),
        "precipitation": current.Variables(7).Value(),
        "uv_index": daily.Variables(0).ValuesAsNumpy()[0] # Get today's max UV
    }

    return weather