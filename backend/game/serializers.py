from rest_framework import serializers
from .models import GameWorld, Farm
from .climate import get_hemisphere, get_climate_zone
from .farm_environment import initialize_farm_environment


class GameWorldSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameWorld
        fields = [
            'id',
            'current_date',
            'game_days_per_real_day',
            'is_running',
            'last_real_update',
            'world_seed',
        ]

class FarmCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "country",
            "region",
            "climate_zone",
            "hemisphere",
            "timezone",
            "elevation",
            "natural_soil_type",
            "natural_soil_ph",
            "natural_soil_fertility",
            "natural_soil_moisture",
            "natural_soil_organic_matter",
            "natural_nitrogen",
            "natural_phosphorus",
            "natural_potassium",
            "soil_data_source",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "country",
            "region",
            "climate_zone",
            "hemisphere",
            "timezone",
            "elevation",
            "natural_soil_type",
            "natural_soil_ph",
            "natural_soil_fertility",
            "natural_soil_moisture",
            "natural_soil_organic_matter",
            "natural_nitrogen",
            "natural_phosphorus",
            #"natural_soil_data_source",
            "soil_data_source",
            "created_at",
        ]

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )
        return value

    def create(self, validated_data):
        owner = validated_data.pop("owner")

        latitude = float(validated_data["latitude"])
        longitude = float(validated_data["longitude"])

        validated_data["hemisphere"] = get_hemisphere(latitude)
        validated_data["climate_zone"] = get_climate_zone(
            latitude,
            longitude,
        )

        farm = Farm.objects.create(
            owner=owner,
            **validated_data,
        )

        initialize_farm_environment(farm)

        return farm