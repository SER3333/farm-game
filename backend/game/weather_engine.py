
import hashlib
import random
from datetime import timedelta

from django.db import transaction

from .climate import get_default_climate_profile
from .models import Farm, GameWorld, WeatherDay
from .weather import get_current_weather


WEATHER_TYPES = {
    "clear": "Ясно",
    "partly_cloudy": "Мінлива хмарність",
    "cloudy": "Хмарно",
    "rain": "Дощ",
    "heavy_rain": "Сильний дощ",
    "snow": "Сніг",
    "sleet": "Мокрий сніг",
    "fog": "Туман",
    "storm": "Гроза",
}


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def get_weather_seed(world_seed, farm, game_date):
    value = (
        f"{world_seed}:"
        f"{farm.latitude}:"
        f"{farm.longitude}:"
        f"{game_date.isoformat()}"
    )
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _get_weather_type(temperature, precipitation, cloud, humidity, rng):
    if humidity >= 94 and cloud >= 75 and rng.random() < 0.25:
        return "fog"

    if precipitation > 0:
        if temperature <= 0:
            return "snow"
        if temperature <= 2:
            return "sleet"
        if precipitation >= 15:
            if temperature >= 18 and rng.random() < 0.12:
                return "storm"
            return "heavy_rain"
        if temperature >= 18 and rng.random() < 0.08:
            return "storm"
        return "rain"

    if cloud < 25:
        return "clear"
    if cloud < 60:
        return "partly_cloudy"
    return "cloudy"


def _store_weather(farm, game_date, data):
    record, _ = WeatherDay.objects.update_or_create(
        farm=farm,
        date=game_date,
        defaults={"weather_data": data},
    )
    return record.weather_data


def initialize_farm_weather(farm, game_date, world_seed=None):
    """
    Створює початкову погоду ферми на дату старту.
    Викликається один раз під час створення ферми.
    """
    existing = WeatherDay.objects.filter(
        farm=farm,
        date=game_date,
    ).first()

    if existing:
        return existing.weather_data

    if world_seed is None:
        world = GameWorld.objects.first()
        world_seed = world.world_seed if world else 20260930

    climate = get_default_climate_profile(
        farm.latitude,
        farm.longitude,
    )

    try:
        observed = get_current_weather(
            farm.latitude,
            farm.longitude,
        )
    except Exception:
        observed = {}

    month = game_date.month
    rng = random.Random(
        get_weather_seed(world_seed, farm, game_date)
    )

    temperature = float(
        observed.get(
            "temperature",
            climate.monthly_temperature[month],
        )
    )
    humidity = float(
        observed.get(
            "humidity",
            climate.monthly_humidity[month],
        )
    )
    precipitation = float(
        observed.get("rainfall_mm", 0.0)
    )
    cloud = float(
        observed.get(
            "cloud_cover",
            climate.monthly_cloud_cover[month],
        )
    )
    wind_speed = float(
        observed.get(
            "wind_speed",
            climate.monthly_wind_speed[month],
        )
    )
    wind_direction = observed.get(
        "wind_direction",
        rng.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
    )

    weather_type = _get_weather_type(
        temperature,
        precipitation,
        cloud,
        humidity,
        rng,
    )

    data = {
        "date": game_date.isoformat(),
        "weather_type": weather_type,
        "weather_name": WEATHER_TYPES[weather_type],
        "temperature": round(temperature, 1),
        "precipitation": round(precipitation, 1),
        "rainfall_mm": round(precipitation, 1),
        "cloud_cover": round(cloud, 1),
        "humidity": round(humidity, 1),
        "wind_speed": round(wind_speed, 1),
        "wind_direction": wind_direction,
        "weather_code": int(observed.get("weather_code", 1)),
        "climate_zone": climate.climate_zone,
        "hemisphere": climate.hemisphere,
        "source": "initial_observation",
    }

    return _store_weather(farm, game_date, data)


def _generate_next_day(farm, previous_data, game_date, world_seed):
    climate = get_default_climate_profile(
        farm.latitude,
        farm.longitude,
    )

    previous_date = game_date - timedelta(days=1)
    previous_month = previous_date.month
    month = game_date.month

    seed = get_weather_seed(world_seed, farm, game_date)
    rng = random.Random(seed)

    # Температура: сезонна норма + частина попереднього відхилення.
    normal_temp = climate.monthly_temperature[month]
    previous_normal = climate.monthly_temperature[previous_month]

    previous_anomaly = (
        float(previous_data["temperature"]) - previous_normal
    )

    temperature = (
        normal_temp
        + previous_anomaly * 0.65
        + rng.uniform(-2.5, 2.5)
    )

    # Хмарність має інерцію: не змінюється повністю випадково.
    normal_cloud = climate.monthly_cloud_cover[month]
    cloud = clamp(
        float(previous_data["cloud_cover"]) * 0.65
        + normal_cloud * 0.35
        + rng.uniform(-18, 18),
        0,
        100,
    )

    # Опади: місячна середня добова кількість задає масштаб.
    mean_daily_precipitation = max(
        climate.monthly_precipitation[month],
        0.1,
    )

    rain_probability = clamp(
        0.10 + mean_daily_precipitation / 8.0
        + cloud / 250.0,
        0.05,
        0.75,
    )

    precipitation = 0.0

    if rng.random() < rain_probability:
        precipitation = rng.expovariate(
            1.0 / max(mean_daily_precipitation, 0.5)
        )
        precipitation = round(
            clamp(precipitation, 0.5, 40.0),
            1,
        )

    # Вологість залежить від регіональної норми, хмарності й опадів.
    normal_humidity = climate.monthly_humidity[month]
    humidity = clamp(
        normal_humidity * 0.5
        + float(previous_data["humidity"]) * 0.2
        + cloud * 0.2
        + (15 if precipitation > 0 else 0)
        + rng.uniform(-8, 8),
        20,
        100,
    )

    # Вітер також має часткову інерцію.
    normal_wind = climate.monthly_wind_speed[month]
    wind_speed = clamp(
        float(previous_data["wind_speed"]) * 0.55
        + normal_wind * 0.45
        + rng.uniform(-8, 8),
        0,
        100,
    )

    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    previous_direction = previous_data.get("wind_direction", "W")

    if rng.random() < 0.65:
        wind_direction = previous_direction
    else:
        wind_direction = rng.choice(directions)

    weather_type = _get_weather_type(
        temperature,
        precipitation,
        cloud,
        humidity,
        rng,
    )

    # Спрощений WMO-код для сумісності з іншими частинами гри.
    weather_codes = {
        "clear": 0,
        "partly_cloudy": 2,
        "cloudy": 3,
        "fog": 45,
        "rain": 61,
        "heavy_rain": 65,
        "snow": 71,
        "sleet": 66,
        "storm": 95,
    }

    return {
        "date": game_date.isoformat(),
        "weather_type": weather_type,
        "weather_name": WEATHER_TYPES[weather_type],
        "temperature": round(temperature, 1),
        "precipitation": precipitation,
        "rainfall_mm": precipitation,
        "cloud_cover": round(cloud, 1),
        "humidity": round(humidity, 1),
        "wind_speed": round(wind_speed, 1),
        "wind_direction": wind_direction,
        "weather_code": weather_codes[weather_type],
        "climate_zone": climate.climate_zone,
        "hemisphere": climate.hemisphere,
        "source": "simulation",
    }


def get_daily_weather(farm, game_date, world_seed=None):
    """
    Повертає збережену погоду на дату або генерує
    від останнього збереженого дня до потрібної дати.
    """
    existing = WeatherDay.objects.filter(
        farm=farm,
        date=game_date,
    ).first()

    if existing:
        return existing.weather_data

    if world_seed is None:
        world = GameWorld.objects.first()
        world_seed = world.world_seed if world else 20260930

    previous_record = (
        WeatherDay.objects
        .filter(farm=farm, date__lt=game_date)
        .order_by("-date")
        .first()
    )

    if previous_record is None:
        return initialize_farm_weather(
            farm,
            game_date,
            world_seed,
        )

    current_date = previous_record.date
    current_data = previous_record.weather_data

    while current_date < game_date:
        next_date = current_date + timedelta(days=1)

        already_generated = WeatherDay.objects.filter(
            farm=farm,
            date=next_date,
        ).first()

        if already_generated:
            current_data = already_generated.weather_data
        else:
            current_data = _generate_next_day(
                farm,
                current_data,
                next_date,
                world_seed,
            )
            _store_weather(farm, next_date, current_data)

        current_date = next_date

    return current_data