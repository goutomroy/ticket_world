from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.reservations.models import ReservationEventSeat


class ReservationEventSeatSerializer(serializers.ModelSerializer):
    object_permissions = DRYPermissionsField()

    class Meta:
        model = ReservationEventSeat
        fields = (
            "id",
            "reservation",
            "event_seat",
            "object_permissions",
        )
        read_only_fields = (
            "id",
            "object_permissions",
            "created",
            "updated",
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ReservationEventSeat.objects.all(),
                fields=["reservation", "event_seat"],
            )
        ]

    def validate_reservation(self, reservation):
        result, message = reservation.is_valid()
        if result is False:
            raise serializers.ValidationError(message)
        return reservation

    def validate_event_seat(self, event_seat):
        if event_seat.is_reserved():
            raise serializers.ValidationError(_("Seat is already reserved."))
        return event_seat
