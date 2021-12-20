from django.urls import re_path, path, include
from rest_framework.routers import SimpleRouter

from apps.reservations.views import ReservationViewSet, ReservationVenueSeatViewSet

app_name = "reservations"

reservation_router = SimpleRouter(trailing_slash=False)
reservation_router.register(r"reservations", ReservationViewSet)
reservation_router.register(r"reservation_venue_seats", ReservationVenueSeatViewSet)

urlpatterns = reservation_router.urls

