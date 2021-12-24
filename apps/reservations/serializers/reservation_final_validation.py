from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.events.models import EventSeat


class FinalReservationValidationListSerializer(serializers.ListSerializer):
    def validate_even_number_of_seats(self, attrs):
        if len(attrs) % 2 != 0:
            self.custom_non_field_errors.append(
                _("You can only buy tickets in quantity that is even")
            )

    def validate_all_seats_around_each_other(self, attrs):
        seat_numbers = sorted([event_seat.seat_number for event_seat in attrs])
        first_seat_number = seat_numbers[0]
        for each in seat_numbers[1:]:
            if each - first_seat_number > 1:
                self.custom_non_field_errors.append(
                    _("All seats should be around each other")
                )
                break
            first_seat_number = each

    def validate(self, attrs):
        self.custom_non_field_errors = []
        self.validate_even_number_of_seats(attrs)
        self.validate_all_seats_around_each_other(attrs)

        # TODO:  avoid one - we can only buy tickets in a quantity that will not leave only 1 ticket # noqa
        if self.custom_non_field_errors:
            raise serializers.ValidationError(self.custom_non_field_errors)


class FinalReservationValidationSerializer(serializers.Serializer):
    event_seat = serializers.PrimaryKeyRelatedField(
        queryset=EventSeat.objects.all(),
    )

    class Meta:
        list_serializer_class = FinalReservationValidationListSerializer
        field = "__all__"

    def validate_event_seat(self, event_seat):
        if event_seat.is_reserved():
            raise serializers.ValidationError(_("Seat is already reserved."))
        return event_seat
