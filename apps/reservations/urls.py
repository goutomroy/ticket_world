from rest_framework.routers import SimpleRouter

from apps.reservations.views import ReservationEventSeatViewSet, ReservationViewSet

app_name = "reservations"

reservation_router = SimpleRouter(trailing_slash=False)
reservation_router.register(r"reservations", ReservationViewSet)
reservation_router.register(r"reservation_event_seats", ReservationEventSeatViewSet)

urlpatterns = reservation_router.urls

# >>> from rest_framework.reverse import reverse
# >>> reverse("reservations:ticket", kwargs={"pk": "45"})
