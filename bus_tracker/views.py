from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LocationPing

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_ping(request, trip_id):
    ping = LocationPing.objects.filter(
        trip_id=trip_id
    ).order_by('-timestamp').first()

    if not ping:
        return Response({})

    return Response({
        "lat": ping.lat,
        "lon": ping.lon
    })
