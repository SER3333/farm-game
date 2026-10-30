import requests
from .soil import get_soil_data

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_location_data(latitude, longitude):
    """
    Отримує країну та адміністративний регіон за координатами.
    """
    response = requests.get(
        NOMINATIM_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "zoom": 10,
            "addressdetails": 1,
        },
        headers={
            "User-Agent": "FarmGame/1.0"
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()
    address = data.get("address", {})

    return {
        "country": address.get("country", ""),
        "region": (
            address.get("state")
            or address.get("region")
            or address.get("province")
            or ""
        ),
    }


def get_weather_location_data(latitude, longitude):
    """
    Отримує timezone та висоту над рівнем моря
    для координат ферми через Open-Meteo.
    """
    response = requests.get(
        OPEN_METEO_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return {
        "timezone": data.get("timezone", ""),
        "elevation": data.get("elevation"),
        "utc_offset_seconds": data.get("utc_offset_seconds"),
    }


def get_elevation(latitude, longitude):
    """
    Отримує висоту над рівнем моря.
    """
    data = get_weather_location_data(latitude, longitude)
    return data["elevation"]


def get_timezone(latitude, longitude):
    """
    Отримує часовий пояс за координатами.
    """
    data = get_weather_location_data(latitude, longitude)
    return data["timezone"]



def initialize_farm_environment(farm):
    """
    Ініціалізує географічне середовище та початковий профіль ґрунту.
    """
    latitude = float(farm.latitude)
    longitude = float(farm.longitude)

    location = get_location_data(latitude, longitude)
    weather_location = get_weather_location_data(latitude, longitude)
    soil = get_soil_data(
        latitude,
        longitude,
        farm.climate_zone,
    )

    farm.country = location["country"]
    farm.region = location["region"]
    farm.timezone = weather_location["timezone"]
    farm.elevation = weather_location["elevation"]

    farm.natural_soil_type = soil.soil_type
    farm.natural_soil_ph = soil.ph
    farm.natural_soil_fertility = soil.fertility
    farm.natural_soil_organic_matter = soil.organic_matter
    farm.natural_soil_moisture = soil.moisture
    farm.natural_nitrogen = soil.nitrogen
    farm.natural_phosphorus = soil.phosphorus
    farm.natural_potassium = soil.potassium
    farm.soil_data_source = soil.source

    farm.save(
        update_fields=[
            "country",
            "region",
            "timezone",
            "elevation",
            "natural_soil_type",
            "natural_soil_ph",
            "natural_soil_fertility",
            "natural_soil_moisture",
            "natural_nitrogen",
            "natural_phosphorus",
            "natural_potassium",
            "soil_data_source",
            "natural_soil_organic_matter",
        ]
    )

    return farm