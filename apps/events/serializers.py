import datetime

import pytz
from django.db.models import Q
from dry_rest_permissions.generics import DRYPermissionsField
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.events.models import Event, EventTag, EventSeatType, EventSeat


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


class EventTagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, event_tag):
        return EventTagSerializer(event_tag).data


class EventSerializer(serializers.ModelSerializer):
    _default_custom_error_message = {
        "venue_start_date_end_date": {"venue_start_date_end_date": _("Venue is occupied by other event right now")},
        "start_date_end_date": {"start_date_end_date": _("end_date must be grater than start_date")},
        "start_date": {"start_date": _("start_date cant be grater than current end_date")},
        "end_date": {"end_date": _("end_date cant be less than current start_date")},
        "venue": {"venue": _("Venue is occupied by other event right now")},
    }

    object_permissions = DRYPermissionsField()
    tags = EventTagPrimaryKeyRelatedField(many=True, queryset=EventTag.objects.all())

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "user",
            "venue",
            "tags",
            "status",
            "start_date",
            "end_date",
            "object_permissions",
            "created",
            "updated",
        )
        read_only_fields = (
            "id",
            'user',
            "slug",
            'object_permissions',
            "created",
            "updated",
        )

    def get_extra_kwargs(self):
        kwargs = super().get_extra_kwargs()
        if self.context["view"].action in ["partial_update"]:
            kwargs["status"] = {"required": True}
        return kwargs

    def validate_start_date(self, value):
        if value < datetime.datetime.now(tz=pytz.UTC):
            raise serializers.ValidationError(_("Must be a future datetime"))
        return value

    def validate_end_date(self, value):
        if value < datetime.datetime.now(tz=pytz.UTC):
            raise serializers.ValidationError(_("Must be a future datetime"))
        return value

    def validate_status(self, value):
        if value < self.instance.status:
            raise serializers.ValidationError(_("status can't be downgrade"))
        return value

    def validate_venue_for_partial_update(self, data):
        if Event.objects.filter(
                ~Q(id=self.instance.id) &
                Q(venue=data["venue"]) &
                (
                        Q(start_date__lte=self.instance.start_date, end_date__gte=self.instance.start_date) |
                        Q(start_date__lte=self.instance.end_date, end_date__gte=self.instance.end_date)
                )
        ).exists():
            self._object_level_validation_errors.append(self._default_custom_error_message["venue"])

    def validate_start_date_for_partial_update(self, data):
        if data["start_date"] > self.instance.end_date:
            self._object_level_validation_errors.append(self._default_custom_error_message["start_date"])

    def validate_end_date_for_partial_update(self, data):
        if data["end_date"] < self.instance.start_date:
            self._object_level_validation_errors.append(self._default_custom_error_message["end_date"])

    def validate_start_end_date(self, data):
        if data["start_date"] > data["end_date"]:
            self._object_level_validation_errors.append(self._default_custom_error_message["start_date_end_date"])

    def validate_venue_start_end_date_create(self, data):
        if Event.objects.filter(
                Q(venue=data["venue"]) &
                (
                    Q(start_date__lte=data["start_date"], end_date__gte=data["start_date"]) |
                    Q(start_date__lte=data["end_date"], end_date__gte=data["end_date"])
                )

        ).exists():
            self._object_level_validation_errors.append(self._default_custom_error_message["venue_start_date_end_date"])

    def validate_venue_start_end_date_for_update_partial_update(self, data):
        if Event.objects.filter(
                ~Q(id=self.instance.id) &
                Q(venue=data["venue"]) &
                (
                    Q(start_date__lte=data["start_date"], end_date__gte=data["start_date"]) |
                    Q(start_date__lte=data["end_date"], end_date__gte=data["end_date"])
                )
        ).exists():
            self._object_level_validation_errors.append(self._default_custom_error_message["venue_start_date_end_date"])

    def validate(self, data):

        self._object_level_validation_errors = []

        if self.context["view"].action == "create":

            self.validate_start_end_date(data)
            self.validate_venue_start_end_date_create(data)

        elif self.context["view"].action == "update":

            self.validate_start_end_date(data)
            self.validate_venue_start_end_date_for_update_partial_update(data)

        elif self.context["view"].action == "partial_update":

            if all([key in data for key in ["venue", "start_date", "end_date"]]):
                self.validate_start_end_date(data)
                self.validate_venue_start_end_date_for_update_partial_update(data)

            elif all([key in data for key in ["start_date", "end_date"]]):
                self.validate_start_end_date(data)

            elif all([key in data for key in ["start_date"]]):
                self.validate_start_date_for_partial_update(data)

            elif all([key in data for key in ["end_date"]]):
                self.validate_end_date_for_partial_update(data)

            elif all([key in data for key in ["venue"]]):
                self.validate_venue_for_partial_update(data)

        if self._object_level_validation_errors:
            raise serializers.ValidationError(self._object_level_validation_errors)

        return data

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        event = Event.objects.create(**validated_data)
        event.tags.add(*tags)
        return event

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.tags.add(*tags)
        return instance


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
        if value.user != self.context["request"].user or \
                not self.context["request"].user.is_superuser or not self.context["request"].user.is_staff:
            raise serializers.ValidationError(_("Only Creator of event or admin/staff can create, update event seat type"))
        return value


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
        if value.event.user != self.context["request"].user or \
                not self.context["request"].user.is_superuser or not self.context["request"].user.is_staff:
            raise serializers.ValidationError(_("Only Creator of event or admin/staff can create, destroy event seat"))
        return value

