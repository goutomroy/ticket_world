from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.events.models import EventSeatType


class EventSeatTypeSerializer(serializers.ModelSerializer):
    # object_permissions = DRYPermissionsField()

    class Meta:
        model = EventSeatType
        fields = (
            "id",
            "name",
            "event",
            "price",
            "info",
            # 'object_permissions',
        )
        read_only_fields = (
            "id",
            # "object_permissions",
            "created",
            "updated",
        )

    def validate_event(self, value):
        if value.user != self.context["request"].user:
            raise serializers.ValidationError(
                _("Only Creator of event can create, update event seat type")
            )
        return value
