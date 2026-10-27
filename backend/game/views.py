from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import FarmCreateSerializer, GameWorldSerializer
from .models import GameWorld, Farm



@api_view(['GET'])
def world_detail(request):
    world = GameWorld.objects.first()

    if not world:
        return Response(
            {
                'error': 'Game world does not exist.'
            },
            status=404
        )

    serializer = GameWorldSerializer(world)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def farm_create(request):
    if Farm.objects.filter(owner=request.user).exists():
        return Response(
            {"error": "You already have a farm."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = FarmCreateSerializer(data=request.data)

    if serializer.is_valid():
        farm = serializer.save(owner=request.user)

        return Response(
            FarmCreateSerializer(farm).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )