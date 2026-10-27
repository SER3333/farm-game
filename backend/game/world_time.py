from datetime import timedelta

from django.utils import timezone

from .models import GameWorld


def update_world_time():
    world = GameWorld.objects.first()

    if world is None:
        return None

    now = timezone.now()

    if world.is_running:
        real_seconds = (
            now - world.last_real_update
        ).total_seconds()

        real_days = real_seconds / 86400

        game_days = (
            real_days *
            world.game_days_per_real_day
        )

        world.current_date += timedelta(
            days=game_days
        )

    world.last_real_update = now

    world.save(
        update_fields=[
            'current_date',
            'last_real_update',
        ]
    )

    return world.current_date


def get_world_date():
    world = GameWorld.objects.first()

    if world is None:
        return None

    if not world.is_running:
        return world.current_date

    now = timezone.now()

    real_seconds = (
        now - world.last_real_update
    ).total_seconds()

    real_days = real_seconds / 86400

    game_days = (
        real_days *
        world.game_days_per_real_day
    )

    return world.current_date + timedelta(
        days=game_days
    )


def get_current_season():
    world_date = get_world_date()

    if world_date is None:
        return None

    month = world_date.month

    if month in (12, 1, 2):
        return 'winter'

    if month in (3, 4, 5):
        return 'spring'

    if month in (6, 7, 8):
        return 'summer'

    return 'autumn'