from django.urls import path

from .views import world_detail, farm_create


urlpatterns = [
    path('world/', world_detail, name='world-detail'),
    path("farms/", farm_create, name="farm-create"),
]