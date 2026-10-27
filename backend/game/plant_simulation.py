
from math import exp

from django.db import transaction

from .models import Plant, PlantPart


def clamp(value, minimum=0.0, maximum=100.0):
    """Обмежує значення заданим діапазоном."""
    return max(minimum, min(maximum, float(value)))


def get_weather_values(weather_data):
    """
    Перетворює дані Open-Meteo або нормалізований
    словник погоди на єдиний формат.

    rainfall_mm бажано передавати як опади за
    конкретний ігровий день, а не поточну мить.
    """
    current = weather_data.get("current", weather_data)

    temperature = current.get(
        "temperature_2m",
        current.get("temperature", 15.0),
    )

    humidity = current.get(
        "relative_humidity_2m",
        current.get("humidity", 60.0),
    )

    rainfall = weather_data.get(
        "rainfall_mm",
        weather_data.get(
            "precipitation_sum",
            current.get(
                "precipitation",
                current.get("rainfall", 0.0),
            ),
        ),
    )

    wind_speed = current.get(
        "wind_speed_10m",
        current.get("wind_speed", 5.0),
    )

    weather_code = current.get(
        "weather_code",
        current.get("weathercode", 1),
    )

    return {
        "temperature": float(temperature),
        "humidity": clamp(humidity),
        "rainfall_mm": max(0.0, float(rainfall)),
        "wind_speed": max(0.0, float(wind_speed)),
        "weather_code": int(weather_code),
    }


def temperature_factor(crop, temperature):
    """
    Оцінює відповідність температури потребам виду.
    1.0 означає оптимальну температуру.
    """
    minimum = crop.min_temperature
    optimum = crop.optimal_temperature
    maximum = crop.max_temperature

    if temperature <= minimum or temperature >= maximum:
        return 0.0

    if temperature <= optimum:
        denominator = max(optimum - minimum, 0.1)
        return clamp((temperature - minimum) / denominator, 0.0, 1.0)

    denominator = max(maximum - optimum, 0.1)
    return clamp((maximum - temperature) / denominator, 0.0, 1.0)


def sunlight_factor(weather_code):
    """
    Приблизна частка доступного світла за кодом WMO.
    Пізніше її можна замінити даними сонячної радіації.
    """
    if weather_code == 0:
        return 1.0

    if weather_code in (1, 2):
        return 0.8

    if weather_code == 3:
        return 0.55

    if weather_code in (45, 48):
        return 0.4

    if 51 <= weather_code <= 67:
        return 0.45

    if 71 <= weather_code <= 86:
        return 0.4

    if 95 <= weather_code <= 99:
        return 0.3

    return 0.65


def simulate_plant_day(plant_id, weather_data):
    """
    Виконує один крок біологічної симуляції рослини.

    Важливо:
    - один виклик = один ігровий день;
    - час світу ця функція не змінює;
    - погоду отримує ззовні;
    - використовує наявні моделі Plant, Plot,
      Crop та PlantPart.

    Повертає словник із результатами розрахунку.
    """

    weather = get_weather_values(weather_data)

    with transaction.atomic():
        plant = (
            Plant.objects
            .select_for_update()
            .select_related("crop", "plot")
            .get(pk=plant_id)
        )

        crop = plant.crop
        plot = plant.plot

        if plant.health <= 0 or plant.vitality <= 0:
            return {
                "plant_id": plant.pk,
                "status": "dead",
                "reason": "Рослина втратила життєздатність.",
            }

        # -------------------------------------------------
        # 1. ПОГОДА
        # -------------------------------------------------

        temperature = weather["temperature"]
        humidity = weather["humidity"]
        rainfall = weather["rainfall_mm"]
        wind_speed = weather["wind_speed"]

        temp_factor = temperature_factor(crop, temperature)
        light_factor = sunlight_factor(weather["weather_code"])

        # -------------------------------------------------
        # 2. ВОДА В ҐРУНТІ
        # -------------------------------------------------

        # Спрощена оцінка добового випаровування.
        evaporation = (
            0.25
            + max(temperature, 0.0) * 0.025
            + wind_speed * 0.015
            + light_factor * 0.35
        )

        # Один міліметр опадів збільшує ігровий індекс
        # вологості. Це початковий коефіцієнт для калібрування.
        soil_moisture = clamp(
            plot.moisture + rainfall * 1.5 - evaporation
        )

        # -------------------------------------------------
        # 3. ПОТРЕБА РОСЛИНИ У ВОДІ
        # -------------------------------------------------

        water_demand = (
            crop.water_need / 100.0
        ) * (
            1.0 + max(temperature - 15.0, 0.0) * 0.025
        )

        water_demand = clamp(water_demand, 0.2, 4.0)

        # Корені визначають, яку частку води рослина
        # може отримати з доступної вологи ґрунту.
        root_factor = clamp(
            0.25 + plant.root_development * 0.01,
            0.25,
            1.0,
        )

        water_available = (
            soil_moisture / 100.0
        ) * water_demand * root_factor

        water_uptake = min(water_available, water_demand)

        water_reserve = clamp(
            plant.water_reserve
            + water_uptake
            - water_demand
        )

        water_factor = clamp(
            water_reserve / max(water_demand * 10.0, 1.0),
            0.0,
            1.0,
        )

        # -------------------------------------------------
        # 4. ПОЖИВНІ РЕЧОВИНИ
        # -------------------------------------------------

        # Ґрунтові запаси та потреби виду визначають
        # доступність кожного елемента.
        nitrogen_uptake = min(
            plot.nitrogen / 100.0,
            crop.nitrogen_need / 100.0,
        )

        phosphorus_uptake = min(
            plot.phosphorus / 100.0,
            crop.phosphorus_need / 100.0,
        )

        potassium_uptake = min(
            plot.potassium / 100.0,
            crop.potassium_need / 100.0,
        )

        nitrogen_reserve = clamp(
            plant.nitrogen_reserve
            + nitrogen_uptake
            - crop.nitrogen_need / 100.0 * 0.5
        )

        phosphorus_reserve = clamp(
            plant.phosphorus_reserve
            + phosphorus_uptake
            - crop.phosphorus_need / 100.0 * 0.3
        )

        potassium_reserve = clamp(
            plant.potassium_reserve
            + potassium_uptake
            - crop.potassium_need / 100.0 * 0.4
        )

        nutrient_factor = (
            clamp(nitrogen_reserve / 50.0)
            * clamp(phosphorus_reserve / 50.0)
            * clamp(potassium_reserve / 50.0)
        ) ** (1.0 / 3.0)

        # -------------------------------------------------
        # 5. ФОТОСИНТЕЗ
        # -------------------------------------------------

        active_parts = list(
            PlantPart.objects.filter(
                plant=plant,
                is_alive=True,
                is_cut=False,
            )
        )

        # Площу листя беремо з рослини та її живих частин.
        part_leaf_area = sum(
            max(part.leaf_area, 0.0)
            for part in active_parts
        )

        leaf_area = max(plant.leaf_area, part_leaf_area)

        # Фотосинтез неможливий без листя.
        # leaf_area — умовна ігрова величина, не м².
        photosynthesis = (
            leaf_area
            * 0.5
            * light_factor
            * temp_factor
            * water_factor
            * nutrient_factor
            * (plant.photosynthesis_efficiency / 100.0)
        )

        # -------------------------------------------------
        # 6. ЕНЕРГЕТИЧНИЙ БАЛАНС
        # -------------------------------------------------

        maintenance_cost = (
            0.15
            + leaf_area * 0.015
            + plant.root_development * 0.002
        )

        energy_reserve = clamp(
            plant.energy_reserve
            + photosynthesis
            - maintenance_cost
        )

        # -------------------------------------------------
        # 7. СТРЕС
        # -------------------------------------------------

        water_stress = 1.0 - water_factor
        temperature_stress = 1.0 - temp_factor
        nutrient_stress = 1.0 - nutrient_factor

        # Тиск шкідників, хвороб і бур'янів уже зберігається
        # в Plant. Тут враховуємо його в загальному навантаженні.
        pest_stress = plant.pest_pressure / 100.0
        disease_stress = plant.disease_pressure / 100.0
        weed_stress = plant.weed_pressure / 100.0

        total_stress = clamp(
            (
                water_stress * 30.0
                + temperature_stress * 25.0
                + nutrient_stress * 20.0
                + pest_stress * 10.0
                + disease_stress * 10.0
                + weed_stress * 5.0
            )
        )

        if total_stress > 35.0:
            health_change = -(total_stress - 35.0) * 0.02
        else:
            health_change = min(
                (35.0 - total_stress) * 0.01,
                0.2,
            )

        health = clamp(plant.health + health_change)

        vitality_change = (
            (photosynthesis - maintenance_cost) * 0.1
            - total_stress * 0.01
        )

        vitality = clamp(plant.vitality + vitality_change)

        # -------------------------------------------------
        # 8. РІСТ КОРЕНІВ
        # -------------------------------------------------

        root_growth = 0.0

        if (
            energy_reserve > 10.0
            and water_factor > 0.3
            and nutrient_factor > 0.3
        ):
            root_growth = (
                0.05
                * energy_reserve / 100.0
                * water_factor
                * nutrient_factor
            )

        root_development = clamp(
            plant.root_development + root_growth,
            0.0,
            100.0,
        )

        # -------------------------------------------------
        # 9. РІСТ НАЯВНИХ ЧАСТИН
        # -------------------------------------------------

        # Це початковий механізм росту вже створених частин.
        # Створення нових пагонів, бруньок і гілок буде
        # окремим наступним етапом симуляції.
        growing_parts = [
            part for part in active_parts
            if part.active_growth_points > 0
        ]

        growth_budget = max(energy_reserve - 10.0, 0.0) * 0.02

        if growing_parts and growth_budget > 0:
            total_weight = sum(
                max(part.growth_potential, 1.0)
                * max(part.vitality, 1.0) / 100.0
                for part in growing_parts
            )

            for part in growing_parts:
                weight = (
                    max(part.growth_potential, 1.0)
                    * max(part.vitality, 1.0) / 100.0
                )

                share = growth_budget * weight / max(total_weight, 0.1)

                part.growth_progress += (
                    share
                    * crop.growth_rate
                    * water_factor
                    * nutrient_factor
                    * temp_factor
                )

                # Перехід до наступної одиниці довжини.
                # Масштаб умовний і потребуватиме калібрування.
                if part.growth_progress >= 100.0:
                    part.length += 1.0
                    part.growth_progress -= 100.0

                part.age_days += 1

                part.save(
                    update_fields=[
                        "growth_progress",
                        "length",
                        "age_days",
                    ]
                )

        # -------------------------------------------------
        # 10. ЗБЕРЕЖЕННЯ СТАНУ
        # -------------------------------------------------

        plot.moisture = soil_moisture

        # Поглинання поживних речовин зменшує їхній запас
        # у ґрунті. Коефіцієнти поки умовні.
        plot.nitrogen = clamp(
            plot.nitrogen - nitrogen_uptake * 0.1
        )
        plot.phosphorus = clamp(
            plot.phosphorus - phosphorus_uptake * 0.1
        )
        plot.potassium = clamp(
            plot.potassium - potassium_uptake * 0.1
        )

        plot.save(
            update_fields=[
                "moisture",
                "nitrogen",
                "phosphorus",
                "potassium",
            ]
        )

        plant.age_days += 1
        plant.water_reserve = water_reserve
        plant.energy_reserve = energy_reserve
        plant.nitrogen_reserve = nitrogen_reserve
        plant.phosphorus_reserve = phosphorus_reserve
        plant.potassium_reserve = potassium_reserve
        plant.photosynthesis_efficiency = clamp(
            plant.photosynthesis_efficiency
            - max(total_stress - 50.0, 0.0) * 0.01
            + (0.1 if total_stress < 25.0 else 0.0)
        )
        plant.root_development = root_development
        plant.root_health = clamp(
            plant.root_health
            - max(soil_moisture - 90.0, 0.0) * 0.01
            - max(10.0 - soil_moisture, 0.0) * 0.02
        )
        plant.health = health
        plant.vitality = vitality
        plant.stress = total_stress

        plant.save(
            update_fields=[
                "age_days",
                "water_reserve",
                "energy_reserve",
                "nitrogen_reserve",
                "phosphorus_reserve",
                "potassium_reserve",
                "photosynthesis_efficiency",
                "root_development",
                "root_health",
                "health",
                "vitality",
                "stress",
            ]
        )

        return {
            "plant_id": plant.pk,
            "status": "alive",
            "age_days": plant.age_days,
            "temperature": temperature,
            "soil_moisture": round(soil_moisture, 2),
            "water_reserve": round(water_reserve, 2),
            "energy_reserve": round(energy_reserve, 2),
            "nutrient_factor": round(nutrient_factor, 3),
            "photosynthesis": round(photosynthesis, 3),
            "stress": round(total_stress, 2),
            "health": round(health, 2),
            "vitality": round(vitality, 2),
            "root_development": round(root_development, 2),
            "active_parts": len(active_parts),
        }