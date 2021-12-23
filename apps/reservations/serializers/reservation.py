from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from apps.reservations.models import Reservation


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
            "created",
            "updated",
        )
        read_only_fields = (
            "id",
            "object_permissions",
            "user",
            "status",
            "payment_id",
            "ticket_number",
            "created",
            "updated",
        )

    def validate_event(self, event):
        result, message = event.is_eligible_for_reservation()
        if result is False:
            raise serializers.ValidationError(message)
        return event
