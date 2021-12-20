from django.contrib.gis.geos import Point
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers

from apps.venues.models import Venue


class LocationField(serializers.DictField):

    def to_representation(self, value):
        return {"x": value.x, "y": value.y}

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return Point(data["x"], data["y"])


class VenueSerializer(serializers.ModelSerializer):
    object_permissions = DRYPermissionsField()
    location = LocationField(child=serializers.FloatField(), allow_empty=False, required=True)

    class Meta:
        model = Venue
        fields = (
            "id",
            "name",
            "address",
            "location",
            'object_permissions',
            "created",
            "updated",
        )
        read_only_fields = (
            "id",
            "object_permissions",
            "created",
            "updated",
        )

