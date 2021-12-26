from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.events.models import EventSeat
from apps.events.serializers import EventSeatTypeSerializer


class EventSeatSerializer(serializers.ModelSerializer):
    event_seat_type = EventSeatTypeSerializer()

    class Meta:
        model = EventSeat
        fields = (
            "id",
            "event_seat_type",
            "seat_number",
        )
        read_only_fields = (
            "id",
            "created",
            "updated",
        )

    def validate_event_seat_type(self, value):
        if (
            value.event.user != self.context["request"].user
            or not self.context["request"].user.is_superuser
            or not self.context["request"].user.is_staff
        ):
            raise serializers.ValidationError(
                _("Only Creator of event or admin/staff can create, destroy event seat")
            )
        return value
