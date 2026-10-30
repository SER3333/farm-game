
from django.contrib import admin
from .models import (
    Farm,
    Plot,
    Crop,
    Plant,
    PlantPart,
    WeatherDay,
    GameWorld,
)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "plant_type",
        "growth_days",
        "water_need",
        "optimal_temperature",
        "fruiting_potential",
    )

    list_filter = (
        "plant_type",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )

    fieldsets = (
        ("Основна інформація", {
            "fields": (
                "name",
                "plant_type",
                "description",
            )
        }),

        ("Ріст і розвиток", {
            "fields": (
                "growth_days",
                "growth_rate",
                "branching_rate",
                "max_branch_depth",
            )
        }),

        ("Вода", {
            "fields": (
                "water_need",
                "drought_tolerance",
            )
        }),

        ("Живлення", {
            "fields": (
                "nitrogen_need",
                "phosphorus_need",
                "potassium_need",
            )
        }),

        ("Температура", {
            "fields": (
                "min_temperature",
                "optimal_temperature",
                "max_temperature",
                "frost_tolerance",
            )
        }),

        ("Світло", {
            "fields": (
                "light_need",
                "shade_tolerance",
            )
        }),

        ("Коренева система", {
            "fields": (
                "root_growth_rate",
                "root_strength",
            )
        }),

        ("Плодоношення", {
            "fields": (
                "fruiting_start_day",
                "fruiting_duration_days",
                "fruiting_potential",
                "fruit_quality_potential",
                "fruit_resource_priority",
            )
        }),

        ("Стійкість", {
            "fields": (
                "weed_competition_tolerance",
                "pest_resistance",
                "disease_resistance",
            )
        }),

        ("Архітектура рослини", {
            "fields": (
                "natural_branch_angle",
                "natural_branch_length",
                "pruning_response",
            )
        }),
    )


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "country",
        "region",
        "climate_zone",
    )


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "farm",
        "soil_type",
        "fertility",
        "moisture",
    )


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = (
        "crop",
        "plot",
        "age_days",
        "health",
        "growth_stage",
    )


@admin.register(PlantPart)
class PlantPartAdmin(admin.ModelAdmin):
    list_display = (
        "plant",
        "part_type",
        "length",
        "health",
        "is_alive",
    )


@admin.register(WeatherDay)
class WeatherDayAdmin(admin.ModelAdmin):
    list_display = (
        "farm",
        "date",
        "created_at",
    )


@admin.register(GameWorld)
class GameWorldAdmin(admin.ModelAdmin):
    list_display = (
        "current_date",
        "is_running",
        "game_days_per_real_day",
    )
