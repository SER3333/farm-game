from django.db import models
from django.contrib.auth.models import User


class Farm(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='farm'
    )

    name = models.CharField(
        max_length=100,
        default='My Farm'
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    region = models.CharField(
        max_length=100,
        blank=True
    )

    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=5
    )

    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5
    )

    # -------------------------
    # Geographic / climate data
    # -------------------------

    climate_zone = models.CharField(
        max_length=50,
        blank=True
    )

    hemisphere = models.CharField(
        max_length=20,
        blank=True
    )

    timezone = models.CharField(
        max_length=50,
        blank=True
    )

    elevation = models.FloatField(
        null=True,
        blank=True
    )

    # -------------------------
    # Natural soil
    # -------------------------

    natural_soil_type = models.CharField(
        max_length=50,
        blank=True
    )

    natural_soil_ph = models.FloatField(
        null=True,
        blank=True
    )

    natural_soil_fertility = models.FloatField(
        default=50.0
    )

    natural_soil_moisture = models.FloatField(
        default=50.0
    )

    natural_nitrogen = models.FloatField(
        default=50.0
    )

    natural_phosphorus = models.FloatField(
        default=50.0
    )

    natural_potassium = models.FloatField(
        default=50.0
    )

    natural_soil_organic_matter = models.FloatField(
        default=50.0
    )

    soil_data_source = models.CharField(
        max_length=50,
        blank=True
    )

    # -------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Plot(models.Model):
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='plots'
    )

    name = models.CharField(
        max_length=100,
        default='Plot'
    )

    soil_type = models.CharField(
        max_length=50,
        default='loam'
    )

    # Ґрунт
    ph = models.FloatField(
        default=6.5
    )

    nitrogen = models.FloatField(
        default=50.0
    )

    phosphorus = models.FloatField(
        default=50.0
    )

    potassium = models.FloatField(
        default=50.0
    )

    organic_matter = models.FloatField(
        default=50.0
    )

    moisture = models.FloatField(
        default=50.0
    )

    temperature = models.FloatField(
        default=15.0
    )

    drainage = models.FloatField(
        default=50.0
    )

    fertility = models.FloatField(
        default=100.0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.farm.name} — {self.name}'


class Crop(models.Model):
    """
    Біологічні властивості виду рослини.

    Наприклад:
    малина, ожина, виноград, яблуня, черешня, горобина.
    """

    PLANT_TYPES = [
        ('bush', 'Bush'),
        ('tree', 'Tree'),
        ('vine', 'Vine'),
    ]

    name = models.CharField(
        max_length=100,
        unique=True
    )

    plant_type = models.CharField(
        max_length=20,
        choices=PLANT_TYPES,
        default='bush'
    )

    description = models.TextField(
        blank=True
    )

    # ---------------------------------
    # РІСТ
    # ---------------------------------

    growth_days = models.PositiveIntegerField(
        default=30
    )

    growth_rate = models.FloatField(
        default=1.0
    )

    branching_rate = models.FloatField(
        default=1.0
    )

    max_branch_depth = models.PositiveIntegerField(
        default=5
    )

    # ---------------------------------
    # ВОДА
    # ---------------------------------

    water_need = models.FloatField(
        default=50.0
    )

    drought_tolerance = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # ЖИВЛЕННЯ
    # ---------------------------------

    nitrogen_need = models.FloatField(
        default=50.0
    )

    phosphorus_need = models.FloatField(
        default=50.0
    )

    potassium_need = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # ТЕМПЕРАТУРА
    # ---------------------------------

    min_temperature = models.FloatField(
        default=5.0
    )

    optimal_temperature = models.FloatField(
        default=20.0
    )

    max_temperature = models.FloatField(
        default=30.0
    )

    frost_tolerance = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # СВІТЛО
    # ---------------------------------

    light_need = models.FloatField(
        default=70.0
    )

    shade_tolerance = models.FloatField(
        default=30.0
    )

    # ---------------------------------
    # КОРЕНЕВА СИСТЕМА
    # ---------------------------------

    root_growth_rate = models.FloatField(
        default=1.0
    )

    root_strength = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # ПЛОДОНОШЕННЯ
    # ---------------------------------

    fruiting_start_day = models.PositiveIntegerField(
        default=30
    )

    fruiting_duration_days = models.PositiveIntegerField(
        default=30
    )

    fruiting_potential = models.FloatField(
        default=100.0
    )

    fruit_quality_potential = models.FloatField(
        default=100.0
    )

    # ---------------------------------
    # БУР'ЯНИ
    # ---------------------------------

    weed_competition_tolerance = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # ШКІДНИКИ
    # ---------------------------------

    pest_resistance = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # ХВОРОБИ
    # ---------------------------------

    disease_resistance = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # СИСТЕМА РОЗГАЛУЖЕННЯ
    # ---------------------------------

    natural_branch_angle = models.FloatField(
        default=45.0
    )

    natural_branch_length = models.FloatField(
        default=100.0
    )

    # Наскільки рослина реагує
    # на обрізування утворенням
    # нових пагонів.
    pruning_response = models.FloatField(
        default=50.0
    )

    # Наскільки сильно рослина
    # спрямовує ресурси до плодів.
    fruit_resource_priority = models.FloatField(
        default=50.0
    )

    def __str__(self):
        return self.name


class Plant(models.Model):
    """
    Конкретна жива рослина.

    Crop = біологія виду.
    Plant = конкретний екземпляр цього виду.
    """

    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name='plants'
    )

    crop = models.ForeignKey(
        Crop,
        on_delete=models.PROTECT,
        related_name='plants'
    )

    planted_at = models.DateTimeField(
        auto_now_add=True
    )

    # ---------------------------------
    # ВІК І РОЗВИТОК
    # ---------------------------------

    age_days = models.PositiveIntegerField(
        default=0
    )

    growth_stage = models.PositiveIntegerField(
        default=0
    )

    development_progress = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # ЗАГАЛЬНИЙ СТАН
    # ---------------------------------

    health = models.FloatField(
        default=100.0
    )

    stress = models.FloatField(
        default=0.0
    )

    vitality = models.FloatField(
        default=100.0
    )

    # ---------------------------------
    # РЕСУРСИ РОСЛИНИ
    # ---------------------------------

    water_reserve = models.FloatField(
        default=50.0
    )

    energy_reserve = models.FloatField(
        default=50.0
    )

    nitrogen_reserve = models.FloatField(
        default=50.0
    )

    phosphorus_reserve = models.FloatField(
        default=50.0
    )

    potassium_reserve = models.FloatField(
        default=50.0
    )

    # ---------------------------------
    # КОРЕНІ
    # ---------------------------------

    root_health = models.FloatField(
        default=100.0
    )

    root_development = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # ФОТОСИНТЕЗ / ЛИСТЯ
    # ---------------------------------

    leaf_area = models.FloatField(
        default=0.0
    )

    photosynthesis_efficiency = models.FloatField(
        default=100.0
    )

    # ---------------------------------
    # ПЛОДОНОШЕННЯ
    # ---------------------------------

    fruit_bud_count = models.PositiveIntegerField(
        default=0
    )

    flower_count = models.PositiveIntegerField(
        default=0
    )

    fruit_count = models.PositiveIntegerField(
        default=0
    )

    harvest_potential = models.FloatField(
        default=0.0
    )

    harvest_quality = models.FloatField(
        default=0.0
    )

    harvest_ready = models.BooleanField(
        default=False
    )

    # ---------------------------------
    # СТАН РОСЛИНИ
    # ---------------------------------

    pest_pressure = models.FloatField(
        default=0.0
    )

    disease_pressure = models.FloatField(
        default=0.0
    )

    weed_pressure = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # ОРІЄНТАЦІЯ РОСЛИНИ
    # ---------------------------------

    height = models.FloatField(
        default=0.0
    )

    canopy_width = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # МЕТАДАНІ
    # ---------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'{self.crop.name} — {self.plot.name}'


class PlantPart(models.Model):
    """
    Окрема частина конкретної рослини.

    Наприклад:
    - стовбур
    - основна гілка
    - пагін
    - бічний пагін
    - точка росту
    - плодова гілка
    """

    PART_TYPES = [
        ('trunk', 'Trunk'),
        ('main_branch', 'Main Branch'),
        ('branch', 'Branch'),
        ('shoot', 'Shoot'),
        ('side_shoot', 'Side Shoot'),
        ('growth_point', 'Growth Point'),
        ('fruiting_branch', 'Fruiting Branch'),
    ]

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='parts'
    )

    # Батьківська частина рослини.
    #
    # Наприклад:
    #
    # стовбур
    #   ↓
    # гілка
    #   ↓
    # пагін
    #   ↓
    # точка росту
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    part_type = models.CharField(
        max_length=30,
        choices=PART_TYPES
    )

    # ---------------------------------
    # РОЗТАШУВАННЯ
    # ---------------------------------

    position_x = models.FloatField(
        default=0.0
    )

    position_y = models.FloatField(
        default=0.0
    )

    position_z = models.FloatField(
        default=0.0
    )

    angle = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # РОЗМІРИ
    # ---------------------------------

    length = models.FloatField(
        default=0.0
    )

    thickness = models.FloatField(
        default=1.0
    )

    # ---------------------------------
    # ВІК
    # ---------------------------------

    age_days = models.PositiveIntegerField(
        default=0
    )

    # ---------------------------------
    # СИЛА ЧАСТИНИ
    # ---------------------------------

    health = models.FloatField(
        default=100.0
    )

    vitality = models.FloatField(
        default=100.0
    )

    # ---------------------------------
    # РІСТ
    # ---------------------------------

    growth_potential = models.FloatField(
        default=100.0
    )

    growth_progress = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # РЕСУРСИ
    # ---------------------------------

    water_flow = models.FloatField(
        default=0.0
    )

    nutrient_flow = models.FloatField(
        default=0.0
    )

    energy_flow = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # ЛИСТЯ
    # ---------------------------------

    leaf_count = models.PositiveIntegerField(
        default=0
    )

    leaf_area = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # ТОЧКИ РОСТУ
    # ---------------------------------

    growth_points = models.PositiveIntegerField(
        default=0
    )

    active_growth_points = models.PositiveIntegerField(
        default=0
    )

    # ---------------------------------
    # ПЛОДОНОШЕННЯ
    # ---------------------------------

    fruit_buds = models.PositiveIntegerField(
        default=0
    )

    flowers = models.PositiveIntegerField(
        default=0
    )

    fruits = models.PositiveIntegerField(
        default=0
    )

    # ---------------------------------
    # ОБРІЗУВАННЯ
    # ---------------------------------

    is_cut = models.BooleanField(
        default=False
    )

    cut_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Наскільки сильно був обрізаний
    # конкретний пагін/гілка.
    cut_severity = models.FloatField(
        default=0.0
    )

    # ---------------------------------
    # СТАН
    # ---------------------------------

    is_alive = models.BooleanField(
        default=True
    )

    is_damaged = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f'{self.get_part_type_display()} '
            f'— {self.plant.crop.name}'
        )


class WeatherDay(models.Model):
    """
    Збережений погодний стан конкретної ферми
    за конкретну ігрову дату.
    """

    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="weather_days",
    )

    date = models.DateField()

    weather_data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["farm", "date"],
                name="unique_weather_day_per_farm",
            )
        ]
        ordering = ["date"]

    def __str__(self):
        return f"{self.farm.name} — {self.date}"


class GameWorld(models.Model):
    current_date = models.DateField()

    game_days_per_real_day = models.PositiveIntegerField(
        default=7
    )

    is_running = models.BooleanField(
        default=True
    )

    last_real_update = models.DateTimeField()

    # Загальний seed світу.
    #
    # Використовуватиметься для
    # детермінованої симуляції.
    world_seed = models.BigIntegerField(
        default=20260930
    )

    def __str__(self):
        return f'World — {self.current_date}'