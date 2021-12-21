from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from apps.reservations.models import Reservation, ReservationEventSeat


class ReservationSerializer(serializers.ModelSerializer):
    object_permissions = DRYPermissionsField()

    class Meta:
        model = Reservation
        fields = (
            "id",
            "user",
            "event",
            "status",
            "payment_id",
            "ticket_number",
            "object_permissions",
        )
        read_only_fields = (
            "id",
            "object_permissions",
            "created",
            "updated",
        )


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
