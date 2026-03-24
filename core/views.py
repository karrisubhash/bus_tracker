from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, status
@@ -18,26 +17,29 @@
    LocationPingSerializer
)

# ======================================================
# AUTH
# ======================================================
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@gmail.com",
        password="admin123"
    )
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# ======================================================
# PERMISSIONS
# ======================================================

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


# ======================================================
# TRIPS
# ======================================================

class TripListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
@@ -47,46 +49,8 @@ def get_queryset(self):
        return Trip.objects.all()


# ======================================================
# DRIVER: SEND LOCATION PINGS
# ======================================================
'''from django.utils import timezone

class LocationPingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):
        trip = get_object_or_404(Trip, id=trip_id)

        if request.user.role != "driver" or trip.driver != request.user:
            return Response({"detail": "Not allowed"}, status=403)

        data = request.data.copy()
        data["trip"] = trip_id

        serializer = LocationPingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        ping = serializer.save(trip=trip)

        # Send to WebSocket
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "bus_locations",
            {
                "type": "bus_location",
                "trip_id": trip.id,
                "lat": ping.lat,
                "lon": ping.lon,
                "bus": trip.bus.registration_no,
                "driver": trip.driver.username if trip.driver else "",
                "route": trip.route.name if trip.route else "",
                "has_issue": trip.has_issue
            }
        )

        return Response(serializer.data, status=201)
        '''
from datetime import timedelta
from django.utils import timezone
import random
@@ -152,11 +116,8 @@ def post(self, request, trip_id):

        return Response(serializer.data, status=201)

#==========================delet all

        # ======================================================
# DRIVER: CLAIM TRIP
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@@ -177,9 +138,7 @@ def claim_trip(request, trip_id):
    return Response({"detail": "Trip claimed successfully"})


# ======================================================
# DRIVER: REPORT ISSUE
# ======================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_all_pings(request):
@@ -206,9 +165,7 @@ def report_issue(request, trip_id):
    return Response({"detail": "Issue reported"})


# ======================================================
# DRIVER: END TRIP
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@@ -225,9 +182,7 @@ def end_trip(request, trip_id):
    return Response({"detail": "Trip ended"})


# ======================================================
# STUDENT: MY BUS
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@@ -252,9 +207,7 @@ def my_bus(request):
    })


# ======================================================
# STUDENT: LATEST PING (POLLING)
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@@ -272,9 +225,7 @@ def latest_ping(request, trip_id):
    })


# ======================================================
# STUDENT: ROUTE PATH
# ======================================================

@api_view(['GET'])
@permission_classes([])
@@ -287,9 +238,8 @@ def route_path(request, trip_id):
    return Response({"path": trip.route.path})


# ======================================================
# ADMIN: ALL TRIPS (TABLE)
# ======================================================


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
@@ -316,41 +266,8 @@ def admin_all_trips(request):
    return Response(data)


# ======================================================
# ADMIN: LIVE MAP (ALL ONGOING BUSES)
# ======================================================
'''from django.db import connection
@api_view(["GET"])
@permission_classes([])
def admin_live_locations(request):

    trips = Trip.objects.filter(status="ongoing").select_related(
        "bus", "route", "driver"
    )

    result = []

    for trip in trips:

        ping = LocationPing.objects.filter(
            trip=trip
        ).order_by("-timestamp").first()

        if not ping:
            continue

        result.append({
            "trip_id": trip.id,
            "bus": trip.bus.registration_no if trip.bus else "",
            "route": trip.route.name if trip.route else "",
            "driver": trip.driver.username if trip.driver else "",
            "lat": ping.lat,
            "lon": ping.lon,
            "has_issue": trip.has_issue,
        })

    return Response(result)# ======================================================
    '''
@api_view(["GET"])
@permission_classes([])
def admin_live_locations(request):
@@ -379,7 +296,6 @@ def admin_live_locations(request):

    return Response(result)
# ADMIN: ONGOING TRIPS (SUMMARY TABLE)
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
@@ -410,9 +326,7 @@ def admin_live_view(request):

def admin_table_view(request):
    return render(request, "admin_table.html")
# ======================================================
# ADMIN: COMPLETED TRIPS
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
@@ -437,9 +351,7 @@ def admin_completed_trips(request):

    return Response(data)

# ======================================================
# DRIVER: RESOLVE ISSUE
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@@ -456,8 +368,3 @@ def resolve_issue(request, trip_id):
    return Response({"detail": "Issue resolved"})
def admin_dashboard_view(request):
    return render(request, "admin_dashboard.html")
from django.shortcuts import render

def driver_page(request):
    return render(request, "driver.html")
    from channels.layers import get_channel_layer
