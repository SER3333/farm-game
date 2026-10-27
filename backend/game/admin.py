from django.contrib import admin

from .models import (
    Farm,
    Plot,
    Crop,
    Plant,
    PlantPart,
    GameWorld,
    WeatherDay,
)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'country',
        'region',
        'climate_zone',
        'hemisphere',
        'created_at',
    )

    search_fields = (
        'name',
        'owner__username',
        'country',
        'region',
    )


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'farm',
        'soil_type',
        'ph',
        'fertility',
        'moisture',
        'temperature',
    )

    list_filter = (
        'soil_type',
    )

    search_fields = (
        'name',
        'farm__name',
    )


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'plant_type',
        'growth_days',
        'water_need',
        'fruiting_potential',
        'pest_resistance',
        'disease_resistance',
    )

    list_filter = (
        'plant_type',
    )

    search_fields = (
        'name',
    )


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = (
        'crop',
        'plot',
        'age_days',
        'growth_stage',
        'health',
        'stress',
        'vitality',
        'fruit_count',
        'harvest_ready',
    )

    list_filter = (
        'harvest_ready',
        'crop',
    )

    search_fields = (
        'crop__name',
        'plot__name',
    )


@admin.register(PlantPart)
class PlantPartAdmin(admin.ModelAdmin):
    list_display = (
        'plant',
        'part_type',
        'parent',
        'age_days',
        'health',
        'length',
        'thickness',
        'is_cut',
        'is_alive',
    )

    list_filter = (
        'part_type',
        'is_cut',
        'is_alive',
        'is_damaged',
    )

    search_fields = (
        'plant__crop__name',
        'plant__plot__name',
    )


@admin.register(WeatherDay)
class WeatherDayAdmin(admin.ModelAdmin):
    list_display = (
        "farm",
        "date",
        "created_at",
    )

    list_filter = (
        "date",
    )

    search_fields = (
        "farm__name",
        "farm__owner__username",
    )

    ordering = (
        "-date",
    )


@admin.register(GameWorld)
class GameWorldAdmin(admin.ModelAdmin):
    list_display = (
        'current_date',
        'game_days_per_real_day',
        'is_running',
        'world_seed',
        'last_real_update',
    )