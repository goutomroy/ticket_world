from django.conf import settings
from django.urls import path
from rest_framework.routers import SimpleRouter

from apps.reservations.views import (
    FinalReservationValidationView,
    ReservationEventSeatViewSet,
    ReservationPaymentSuccessfulView,
    ReservationTicketView,
    ReservationViewSet,
)

app_name = "reservations"

reservation_router = SimpleRouter(trailing_slash=False)
reservation_router.register(r"reservations", ReservationViewSet)
reservation_router.register(r"reservation_event_seats", ReservationEventSeatViewSet)

urlpatterns = [
    *reservation_router.urls,
    # path(
    #     f"events/<uuid:event_id>/", include(reservation_router.urls,)
    # ),
    path(
        f"reservations/<uuid:{settings.RESERVATION_ID_URL_KEY}>/final_validation",
        FinalReservationValidationView.as_view(),
        name="reservation-final-validation",
    ),
    path(
        f"reservations/<uuid:{settings.RESERVATION_ID_URL_KEY}>/payment_successful",
        ReservationPaymentSuccessfulView.as_view(),
        name="reservation-payment-successful",
    ),
    path(
        f"reservations/<uuid:{settings.RESERVATION_ID_URL_KEY}>/ticket",
        ReservationTicketView.as_view(),
        name="reservation-ticket",
    ),
]
