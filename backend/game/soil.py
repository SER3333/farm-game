
from dataclasses import dataclass


@dataclass(frozen=True)
class SoilData:
    """Уніфікований профіль ґрунту для ігрової симуляції."""

    soil_type: str
    ph: float | None

    nitrogen: float
    phosphorus: float
    potassium: float

    fertility: float
    moisture: float

    source: str


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Обмежує ігрове значення діапазоном 0–100."""
    return max(minimum, min(value, maximum))


def calculate_fertility(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
) -> float:
    """Початкова спрощена оцінка родючості за NPK."""
    return round((nitrogen + phosphorus + potassium) / 3.0, 2)


def get_fallback_soil() -> SoilData:
    """
    Тимчасовий нейтральний профіль, якщо дані джерела недоступні.

    Це ігрові значення за замовчуванням, а не реальні вимірювання.
    """
    nitrogen = 50.0
    phosphorus = 50.0
    potassium = 50.0

    return SoilData(
        soil_type="loam",
        ph=6.5,
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        fertility=calculate_fertility(
            nitrogen,
            phosphorus,
            potassium,
        ),
        moisture=50.0,
        source="fallback_default",
    )


def get_soil_data(
    latitude: float,
    longitude: float,
) -> SoilData:
    """
    Єдина точка входу для отримання профілю ґрунту.

    Наступним етапом підключимо глобальне джерело даних
    усередині цієї функції, не змінюючи решту гри.
    """
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    return get_fallback_soil()