from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin
from apps.reservations.serializers import FinalReservationValidationSerializer


class FinalReservationValidationView(ReservationRelatedViewMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reservation_event_seats = self._reservation.get_reservation_event_seats()
        data = [
            {"event_seat": str(event_seat.id)} for event_seat in reservation_event_seats
        ]
        serializer = FinalReservationValidationSerializer(
            data=data, many=True, allow_empty=False
        )
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Valid"})
