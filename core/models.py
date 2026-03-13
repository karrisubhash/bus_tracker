from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone


# ===================== USER =====================

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('student', 'Student'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )

    route = models.ForeignKey(
        'Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ===================== BUS =====================

class Bus(models.Model):
    registration_no = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.registration_no} — {self.name or 'Bus'}"


# ===================== ROUTE (ONLY ONE) =====================

class Route(models.Model):
    name = models.CharField(max_length=100)

    # stops OR path — merged into ONE field
    path = models.JSONField(
        blank=True,null=True)


    def __str__(self):
        return self.name


# ===================== TRIP =====================


class Trip(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(
        'User',
        limit_choices_to={'role': 'driver'},
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trips'
    )
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # 🔴 NEW — ISSUE SYSTEM
    has_issue = models.BooleanField(default=False)
    issue_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Trip {self.id} — {self.bus} — {self.route.name} ({self.status})"

class BusCurrentLocation(models.Model):

    trip = models.OneToOneField(
        "Trip",
        on_delete=models.CASCADE
    )

    lat = models.FloatField()
    lon = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trip} - {self.lat},{self.lon}"

# ===================== LOCATION PING =====================
'''class LocationPing(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="pings")
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

        indexes = [
            models.Index(fields=["trip", "-timestamp"]),
        ]
    

    def __str__(self):
        return f"Ping {self.id} — Trip {self.trip_id}"
'''

class LocationPingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, trip_id):

        # DELETE PINGS OLDER THAN 3 HOURS
        cutoff = timezone.now() - timedelta(hours=3)
        LocationPing.objects.filter(timestamp__lt=cutoff).delete()

        trip = get_object_or_404(Trip, id=trip_id)

        if request.user.role != "driver" or trip.driver != request.user:
            return Response({"detail": "Not allowed"}, status=403)

        data = request.data.copy()
        data["trip"] = trip_id

        serializer = LocationPingSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        ping = serializer.save(trip=trip)

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
