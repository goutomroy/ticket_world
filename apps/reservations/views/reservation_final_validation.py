from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin


class FinalReservationValidationView(ReservationRelatedViewMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def validate_even_number_of_seats(self, reservation_event_seats):
        if len(reservation_event_seats) % 2 != 0:
            self.custom_non_field_errors.append(
                _("You can only buy tickets in quantity that is even")
            )

    def validate_all_seats_around_each_other(self, reservation_event_seats):
        seat_numbers = sorted(
            [
                reservation_event_seat.event_seat.seat_number
                for reservation_event_seat in reservation_event_seats
            ]
        )
        first_seat_number = seat_numbers[0]
        for each in seat_numbers[1:]:
            if each - first_seat_number > 1:
                self.custom_non_field_errors.append(
                    _("All seats should be around each other")
                )
                break
            first_seat_number = each

    def validate(self):
        self.custom_non_field_errors = []
        reservation_event_seats = self._reservation.event_seats.all()
        self.validate_even_number_of_seats(reservation_event_seats)
        self.validate_all_seats_around_each_other(reservation_event_seats)

        # TODO:  avoid one - we can only buy tickets in a quantity that will not leave only 1 ticket # noqa
        if self.custom_non_field_errors:
            raise serializers.ValidationError(self.custom_non_field_errors)

    def get(self, request, *args, **kwargs):
        self.validate()
        # reservation_event_seats = self._reservation.event_seats.values("event_seat")
        # data = [
        #     {"event_seat": str(event_seat["event_seat"])}
        #     for event_seat in reservation_event_seats
        # ]
        # serializer = FinalReservationValidationSerializer(
        #     data=data, many=True, allow_empty=False,
        # )
        # serializer.is_valid(raise_exception=True)
        return Response({"detail": "Valid"})
