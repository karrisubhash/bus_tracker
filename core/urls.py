from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyTokenObtainPairView,
    TripListView,
    LocationPingCreateView,
    claim_trip,
    my_bus,
    latest_ping,
    route_path,
    report_issue,
    end_trip,
    admin_all_trips,
    admin_live_locations,
    admin_ongoing_trips,admin_completed_trips,
    resolve_issue,
    admin_dashboard_view,
driver_page,
)

urlpatterns = [
    # AUTH
    path('token/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),

    # TRIPS
    path('trips/', TripListView.as_view()),
    path('trips/<int:trip_id>/claim/', claim_trip),
    path('trips/<int:trip_id>/pings/', LocationPingCreateView.as_view()),
    path('trips/<int:trip_id>/latest_ping/', latest_ping),
    path('trips/<int:trip_id>/route/', route_path),
    path('trips/<int:trip_id>/issue/', report_issue),
    path('trips/<int:trip_id>/end/', end_trip),
    path("trips/<int:trip_id>/report-issue/", report_issue),
    path('trips/<int:trip_id>/resolve-issue/', resolve_issue),
path("driver/", driver_page),

    # STUDENT
    path('student/my-bus/', my_bus),
    path("admin-panel/dashboard/", admin_dashboard_view),

    # ADMIN APIs
    path('admin/trips/', admin_all_trips),
    path('admin/live-locations/', admin_live_locations),
    path('admin/ongoing-trips/', admin_ongoing_trips),
    path("admin/completed-trips/", admin_completed_trips),
]
