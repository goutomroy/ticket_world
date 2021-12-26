from rest_framework import serializers

from apps.events.models import EventTag


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTag
        fields = (
            "id",
            "name",
            "slug",
        )
        read_only_fields = (
            "id",
            "slug",
            "created",
            "updated",
        )
