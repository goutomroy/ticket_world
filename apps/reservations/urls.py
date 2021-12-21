from rest_framework.routers import SimpleRouter

from apps.reservations.views import ReservationVenueSeatViewSet, ReservationViewSet

app_name = "reservations"

reservation_router = SimpleRouter(trailing_slash=False)
reservation_router.register(r"reservations", ReservationViewSet)
reservation_router.register(r"reservation_event_seats", ReservationVenueSeatViewSet)

urlpatterns = reservation_router.urls
