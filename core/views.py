from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import BusCurrentLocation
from rest_framework_simplejwt.views import TokenObtainPairView
from geopy distance import geodesic
from .models import Trip, LocationPing
from .serializers import (
    MyTokenObtainPairSerializer,
    TripSerializer,
    LocationPingSerializer
)

# ======================================================
# AUTH
# ======================================================

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
    serializer_class = TripSerializer

    def get_queryset(self):
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

class LocationPingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):

        trip = get_object_or_404(Trip, id=trip_id)

        if request.user.role != "driver" or trip.driver != request.user:
            return Response({"detail": "Not allowed"}, status=403)

        # DELETE OLD PINGS OCCASIONALLY
        if random.randint(1,10) == 1:
            cutoff = timezone.now() - timedelta(hours=3)
            LocationPing.objects.filter(timestamp__lt=cutoff).delete()
            last = BusCurrentLocation.objects.filter(trip=trip).first()

            if last:
                old = (last.lat, last.lon)
                new = (float(request.data["lat"]), float(request.data["lon"]))
            
                distance = geodesic(old, new).meters
            
                # Ignore GPS noise
                if distance < 5:
                    return Response({"detail": "Ignored small movement"})

        data = request.data.copy()
        data["trip"] = trip_id

        serializer = LocationPingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        ping = serializer.save(trip=trip)

        # UPDATE CURRENT BUS LOCATION
        BusCurrentLocation.objects.update_or_create(
            trip=trip,
            defaults={
                "lat": ping.lat,
                "lon": ping.lon
            }
        )

        # SEND TO WEBSOCKET
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

#==========================delet all

        # ======================================================
# DRIVER: CLAIM TRIP
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def claim_trip(request, trip_id):
    if request.user.role != 'driver':
        return Response({"detail": "Only drivers allowed"}, status=403)

    trip = get_object_or_404(Trip, id=trip_id)

    if trip.driver and trip.driver != request.user:
        return Response({"detail": "Trip already assigned"}, status=403)

    trip.driver = request.user
    trip.status = "ongoing"
    trip.start_time = timezone.now()
    trip.save()

    return Response({"detail": "Trip claimed successfully"})


# ======================================================
# DRIVER: REPORT ISSUE
# ======================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_all_pings(request):

    deleted, _ = LocationPing.objects.all().delete()

    return Response({
        "message": "All pings deleted",
        "deleted_count": deleted
    })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_issue(request, trip_id):
    
    trip = get_object_or_404(Trip, id=trip_id)

    if request.user.role != "driver" or trip.driver != request.user:
        return Response({"detail": "Not allowed"}, status=403)

    trip.has_issue = True
    trip.issue_text = request.data.get("issue", "")
    trip.save()

    return Response({"detail": "Issue reported"})


# ======================================================
# DRIVER: END TRIP
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.user.role != "driver" or trip.driver != request.user:
        return Response({"detail": "Not allowed"}, status=403)

    trip.status = "completed"
    trip.end_time = timezone.now()
    trip.save()

    return Response({"detail": "Trip ended"})


# ======================================================
# STUDENT: MY BUS
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bus(request):
    if request.user.role != "student":
        return Response({"detail": "Students only"}, status=403)

    if not request.user.route:
        return Response({"detail": "No route assigned"}, status=404)

    trip = Trip.objects.filter(
        route=request.user.route,
        status="ongoing"
    ).first()

    if not trip:
        return Response({"detail": "No active bus"}, status=404)

    return Response({
        "trip_id": trip.id,
        "route": trip.route.name
    })


# ======================================================
# STUDENT: LATEST PING (POLLING)
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_ping(request, trip_id):
    ping = LocationPing.objects.filter(
        trip_id=trip_id
    ).order_by("-timestamp").first()

    if not ping:
        return Response({"detail": "No ping yet"})

    return Response({
        "lat": ping.lat,
        "lon": ping.lon
    })


# ======================================================
# STUDENT: ROUTE PATH
# ======================================================

@api_view(['GET'])
@permission_classes([])
def route_path(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if not trip.route or not trip.route.path:
        return Response({"path": []})

    return Response({"path": trip.route.path})


# ======================================================
# ADMIN: ALL TRIPS (TABLE)
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_all_trips(request):
    trips = Trip.objects.select_related(
        "bus", "route", "driver"
    ).order_by("-start_time")

    data = []

    for trip in trips:
        data.append({
            "trip_id": trip.id,
            "bus": trip.bus.registration_no,
            "route": trip.route.name if trip.route else None,
            "driver": trip.driver.username if trip.driver else None,
            "status": trip.status,
            "start_time": trip.start_time,
            "end_time": trip.end_time,
            "has_issue": trip.has_issue,
            "issue_text": trip.issue_text
        })

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

    locations = BusCurrentLocation.objects.select_related(
        "trip__bus",
        "trip__route",
        "trip__driver"
    ).filter(trip__status="ongoing")

    result = []

    for loc in locations:

        trip = loc.trip

        result.append({
            "trip_id": trip.id,
            "bus": trip.bus.registration_no if trip.bus else "",
            "route": trip.route.name if trip.route else "",
            "driver": trip.driver.username if trip.driver else "",
            "lat": loc.lat,
            "lon": loc.lon,
            "has_issue": trip.has_issue,
        })

    return Response(result)
# ADMIN: ONGOING TRIPS (SUMMARY TABLE)
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_ongoing_trips(request):
    trips = Trip.objects.exclude(status="cancelled")

    data = []

    for trip in trips:
        data.append({
            "trip_id": trip.id,
            "bus": trip.bus.registration_no,
            "route": trip.route.name if trip.route else None,
            "driver": trip.driver.username if trip.driver else None,
            "start_time": trip.start_time,
            "has_issue": trip.has_issue,
            "end_time":trip.end_time
        })

    return Response(data)
def admin_login_page(request):
    return render(request,"admin_login.html")


def admin_live_view(request):
    return render(request, "admin_live.html")


def admin_table_view(request):
    return render(request, "admin_table.html")
# ======================================================
# ADMIN: COMPLETED TRIPS
# ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_completed_trips(request):
    trips = Trip.objects.filter(status="completed").select_related(
        "bus", "route", "driver"
    ).order_by("-end_time")

    data = []

    for trip in trips:
        data.append({
            "trip_id": trip.id,
            "bus": trip.bus.registration_no,
            "route": trip.route.name if trip.route else None,
            "driver": trip.driver.username if trip.driver else None,
            "start_time": trip.start_time,
            "end_time": trip.end_time,
            "has_issue": trip.has_issue,
            "issue_text": trip.issue_text,
        })

    return Response(data)

# ======================================================
# DRIVER: RESOLVE ISSUE
# ======================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_issue(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.user.role != "driver" or trip.driver != request.user:
        return Response({"detail": "Not allowed"}, status=403)

    trip.has_issue = False
    trip.issue_text = ""
    trip.save()

    return Response({"detail": "Issue resolved"})
def admin_dashboard_view(request):
    return render(request, "admin_dashboard.html")
from django.shortcuts import render

def driver_page(request):
    return render(request, "driver.html")
    from channels.layers import get_channel_layer
