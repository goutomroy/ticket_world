from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin
from apps.reservations.serializers import FinalReservationValidationSerializer


class FinalReservationValidationView(ReservationRelatedViewMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        event_seats = self._reservation.get_event_seats()
        data = [
            {
                "event_seat_type": str(event_seat.event_seat_type.id),
                "seat_number": event_seat.seat_number,
            }
            for event_seat in event_seats
        ]
        serializer = FinalReservationValidationSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Valid"})
