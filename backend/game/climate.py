
from dataclasses import dataclass
from datetime import date
import hashlib

import requests
from django.core.cache import cache


ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_hemisphere(latitude):
    return "northern" if float(latitude) >= 0 else "southern"


def get_climate_zone(latitude, longitude=None):
    latitude = abs(float(latitude))

    if latitude < 23.5:
        return "tropical"
    if latitude < 35:
        return "subtropical"
    if latitude < 55:
        return "temperate"
    if latitude < 66.5:
        return "subpolar"
    return "polar"


def get_season(latitude, month):
    hemisphere = get_hemisphere(latitude)

    if hemisphere == "southern":
        month = ((month + 5) % 12) + 1

    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


@dataclass
class ClimateProfile:
    climate_zone: str
    hemisphere: str
    monthly_temperature: dict
    monthly_precipitation: dict
    monthly_humidity: dict
    monthly_cloud_cover: dict
    monthly_wind_speed: dict


def _fallback_profile(latitude, longitude):
    """Грубий резервний профіль, якщо API недоступний."""
    latitude = float(latitude)
    abs_lat = abs(latitude)

    if abs_lat < 23.5:
        base_temp, amplitude = 26.0, 3.0
    elif abs_lat < 35:
        base_temp, amplitude = 18.0, 10.0
    elif abs_lat < 55:
        base_temp, amplitude = 10.0, 15.0
    elif abs_lat < 66.5:
        base_temp, amplitude = 2.0, 18.0
    else:
        base_temp, amplitude = -10.0, 15.0

    temperatures = {}
    precipitation = {}
    humidity = {}
    cloud_cover = {}
    wind_speed = {}

    for month in range(1, 13):
        # Максимум температури припадає на літо відповідної півкулі.
        seasonal_offset = 7.0 * __import__("math").cos(
            2 * __import__("math").pi * (month - 7) / 12
        )
        if latitude < 0:
            seasonal_offset *= -1

        temperatures[month] = base_temp + amplitude / 2 * seasonal_offset / 7
        precipitation[month] = 60.0
        humidity[month] = 65.0
        cloud_cover[month] = 50.0
        wind_speed[month] = 15.0

    return ClimateProfile(
        climate_zone=get_climate_zone(latitude, longitude),
        hemisphere=get_hemisphere(latitude),
        monthly_temperature=temperatures,
        monthly_precipitation=precipitation,
        monthly_humidity=humidity,
        monthly_cloud_cover=cloud_cover,
        monthly_wind_speed=wind_speed,
    )


def get_default_climate_profile(latitude, longitude):
    """
    Кліматичні середні за 1991–2020 роки.

    Результат кешується. Якщо запит не вдався,
    повертається приблизний резервний профіль.
    """
    latitude = round(float(latitude), 3)
    longitude = round(float(longitude), 3)

    key_source = f"{latitude}:{longitude}"
    key_hash = hashlib.sha256(
        key_source.encode("utf-8")
    ).hexdigest()[:24]
    cache_key = f"climate_profile_{key_hash}"

    cached = cache.get(cache_key)
    if cached:
        return ClimateProfile(**cached)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "1991-01-01",
        "end_date": "2020-12-31",
        "daily": (
            "temperature_2m_mean,"
            "precipitation_sum,"
            "relative_humidity_2m_mean,"
            "cloud_cover_mean,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto",
    }

    try:
        response = requests.get(
            ARCHIVE_URL,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        daily = payload["daily"]

        monthly_values = {
            month: {
                "temperature": [],
                "precipitation": [],
                "humidity": [],
                "cloud": [],
                "wind": [],
            }
            for month in range(1, 13)
        }

        for index, day_text in enumerate(daily["time"]):
            month = date.fromisoformat(day_text).month
            values = monthly_values[month]

            def append_if_valid(target, source_key):
                value = daily.get(source_key, [])[index]
                if value is not None:
                    values[target].append(float(value))

            append_if_valid("temperature", "temperature_2m_mean")
            append_if_valid("precipitation", "precipitation_sum")
            append_if_valid("humidity", "relative_humidity_2m_mean")
            append_if_valid("cloud", "cloud_cover_mean")
            append_if_valid("wind", "wind_speed_10m_max")

        def average(values, default):
            return sum(values) / len(values) if values else default

        temperatures = {}
        precipitation = {}
        humidity = {}
        cloud_cover = {}
        wind_speed = {}

        for month, values in monthly_values.items():
            temperatures[month] = average(
                values["temperature"], 15.0
            )
            # Середня кількість опадів за один день у цьому місяці.
            precipitation[month] = average(
                values["precipitation"], 2.0
            )
            humidity[month] = average(
                values["humidity"], 65.0
            )
            cloud_cover[month] = average(
                values["cloud"], 50.0
            )
            wind_speed[month] = average(
                values["wind"], 15.0
            )

        profile = ClimateProfile(
            climate_zone=get_climate_zone(latitude, longitude),
            hemisphere=get_hemisphere(latitude),
            monthly_temperature=temperatures,
            monthly_precipitation=precipitation,
            monthly_humidity=humidity,
            monthly_cloud_cover=cloud_cover,
            monthly_wind_speed=wind_speed,
        )

        cache.set(
            cache_key,
            {
                "climate_zone": profile.climate_zone,
                "hemisphere": profile.hemisphere,
                "monthly_temperature": profile.monthly_temperature,
                "monthly_precipitation": profile.monthly_precipitation,
                "monthly_humidity": profile.monthly_humidity,
                "monthly_cloud_cover": profile.monthly_cloud_cover,
                "monthly_wind_speed": profile.monthly_wind_speed,
            },
            60 * 60 * 24 * 30,
        )

        return profile

    except (
        requests.RequestException,
        KeyError,
        TypeError,
        ValueError,
    ):
        profile = _fallback_profile(latitude, longitude)
        return profile