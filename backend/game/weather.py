
import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_current_weather(latitude, longitude):
    params = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "cloud_cover"
        ),
        "timezone": "auto",
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=10,
    )
    response.raise_for_status()

    payload = response.json()
    current = payload["current"]

    return {
        "temperature": float(current["temperature_2m"]),
        "humidity": float(current["relative_humidity_2m"]),
        "precipitation": float(current["precipitation"]),
        "rainfall_mm": float(current["precipitation"]),
        "weather_code": int(current["weather_code"]),
        "wind_speed": float(current["wind_speed_10m"]),
        "wind_direction": int(current["wind_direction_10m"]),
        "cloud_cover": float(current["cloud_cover"]),
        "observed_at": current.get("time"),
    }

    response.raise_for_status()

    return response.json()
