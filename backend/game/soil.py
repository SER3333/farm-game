

from dataclasses import dataclass
import hashlib
import random


@dataclass(frozen=True)
class SoilData:
    """Початкові характеристики ґрунту для ігрової ферми."""

    soil_type: str
    ph: float

    nitrogen: float
    phosphorus: float
    potassium: float

    organic_matter: float
    fertility: float
    moisture: float

    source: str


# Базові профілі для великих кліматичних зон світу.
# Це умовні ігрові значення, а не реальні вимірювання.
SOIL_PROFILES = {
    "tropical": [
        {
            "type": "clay",
            "ph": 5.5,
            "n": 45,
            "p": 40,
            "k": 50,
            "organic": 55,
            "moisture": 75,
        },
        {
            "type": "loam",
            "ph": 6.0,
            "n": 50,
            "p": 45,
            "k": 50,
            "organic": 60,
            "moisture": 70,
        },
        {
            "type": "sandy_loam",
            "ph": 5.8,
            "n": 40,
            "p": 40,
            "k": 45,
            "organic": 40,
            "moisture": 55,
        },
    ],

    "subtropical": [
        {
            "type": "loam",
            "ph": 6.5,
            "n": 55,
            "p": 50,
            "k": 55,
            "organic": 55,
            "moisture": 55,
        },
        {
            "type": "clay",
            "ph": 7.0,
            "n": 50,
            "p": 45,
            "k": 60,
            "organic": 50,
            "moisture": 65,
        },
        {
            "type": "sandy_loam",
            "ph": 6.3,
            "n": 40,
            "p": 45,
            "k": 50,
            "organic": 40,
            "moisture": 40,
        },
    ],

    "temperate": [
        {
            "type": "loam",
            "ph": 6.5,
            "n": 60,
            "p": 55,
            "k": 60,
            "organic": 65,
            "moisture": 60,
        },
        {
            "type": "clay",
            "ph": 6.8,
            "n": 60,
            "p": 50,
            "k": 55,
            "organic": 60,
            "moisture": 70,
        },
        {
            "type": "sandy_loam",
            "ph": 6.2,
            "n": 45,
            "p": 45,
            "k": 50,
            "organic": 45,
            "moisture": 45,
        },
    ],

    "subpolar": [
        {
            "type": "loam",
            "ph": 5.8,
            "n": 45,
            "p": 40,
            "k": 45,
            "organic": 65,
            "moisture": 70,
        },
        {
            "type": "sandy_loam",
            "ph": 5.5,
            "n": 35,
            "p": 35,
            "k": 40,
            "organic": 45,
            "moisture": 55,
        },
        {
            "type": "peat",
            "ph": 4.8,
            "n": 40,
            "p": 30,
            "k": 35,
            "organic": 85,
            "moisture": 85,
        },
    ],

    "polar": [
        {
            "type": "sandy",
            "ph": 5.5,
            "n": 20,
            "p": 25,
            "k": 25,
            "organic": 20,
            "moisture": 30,
        },
        {
            "type": "peat",
            "ph": 4.8,
            "n": 25,
            "p": 20,
            "k": 25,
            "organic": 75,
            "moisture": 80,
        },
    ],
}


def clamp(value, minimum=0.0, maximum=100.0):
    return max(minimum, min(value, maximum))


def calculate_fertility(
    nitrogen,
    phosphorus,
    potassium,
    organic_matter,
):
    """Спрощена ігрова оцінка родючості."""

    return round(
        nitrogen * 0.30
        + phosphorus * 0.20
        + potassium * 0.20
        + organic_matter * 0.30,
        2,
    )


def get_soil_data(
    latitude,
    longitude,
    climate_zone="temperate",
):
    """
    Створює приблизний профіль ґрунту.

    Для однакових координат результат завжди однаковий.
    """

    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    profiles = SOIL_PROFILES.get(
        climate_zone,
        SOIL_PROFILES["temperate"],
    )

    # Стабільний seed: не змінюється після перезапуску сервера.
    seed_string = (
        f"{latitude:.2f}:"
        f"{longitude:.2f}:"
        f"{climate_zone}"
    )

    seed_hash = hashlib.sha256(
        seed_string.encode("utf-8")
    ).hexdigest()

    rng = random.Random(int(seed_hash[:16], 16))

    # Вибираємо один із можливих профілів.
    profile = rng.choice(profiles)

    # Невеликі відмінності між місцевостями.
    nitrogen = clamp(profile["n"] + rng.uniform(-5, 5))
    phosphorus = clamp(profile["p"] + rng.uniform(-5, 5))
    potassium = clamp(profile["k"] + rng.uniform(-5, 5))

    organic_matter = clamp(
        profile["organic"] + rng.uniform(-5, 5)
    )

    moisture = clamp(
        profile["moisture"] + rng.uniform(-7, 7)
    )

    ph = round(
        profile["ph"] + rng.uniform(-0.3, 0.3),
        2,
    )

    fertility = calculate_fertility(
        nitrogen,
        phosphorus,
        potassium,
        organic_matter,
    )

    return SoilData(
        soil_type=profile["type"],
        ph=ph,
        nitrogen=round(nitrogen, 2),
        phosphorus=round(phosphorus, 2),
        potassium=round(potassium, 2),
        organic_matter=round(organic_matter, 2),
        fertility=fertility,
        moisture=round(moisture, 2),
        source="regional_game_profile",
    )
