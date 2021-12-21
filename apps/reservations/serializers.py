from django.utils.translation import gettext_lazy as _
from dry_rest_permissions.generics import DRYPermissionsField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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


class ReservationEventSeatListSerializer(serializers.ListSerializer):
    def validate_even_number_of_seats(self, attrs):
        if len(attrs) % 2 != 0:
            self.custom_non_field_errors.append(
                _("You can only buy tickets in quantity that is even")
            )

    def validate_all_seats_for_same_reservations(self, attrs):
        reservation_ids = [each["reservation"].id for each in attrs]
        if len(reservation_ids) != reservation_ids.count(reservation_ids[0]):
            self.custom_non_field_errors.append(
                _("You can only reserve seats for a single reservation at a time.")
            )

    def validate_all_seats_around_each_other(self, attrs):
        seat_numbers = sorted([each["event_seat"].seat_number for each in attrs])
        first_seat_number = seat_numbers[0]
        for each in seat_numbers[1:]:
            if each - first_seat_number > 1:
                self.custom_non_field_errors.append(
                    _("All seats should be around each other")
                )
                break

    def validate(self, attrs):
        self.custom_non_field_errors = []
        self.validate_even_number_of_seats(attrs)
        self.validate_all_seats_for_same_reservations(attrs)
        self.validate_all_seats_around_each_other(attrs)
        # TODO:  avoid one - we can only buy tickets in a quantity that will not leave only 1 ticket # noqa
        if self.custom_non_field_errors:
            raise serializers.ValidationError(self.custom_non_field_errors)

        return attrs

    def create(self, validated_data):
        objects = [ReservationEventSeat(**item) for item in validated_data]
        return ReservationEventSeat.objects.bulk_create(objects)


class ReservationEventSeatSerializer(serializers.ModelSerializer):
    object_permissions = DRYPermissionsField()

    class Meta:
        model = ReservationEventSeat
        list_serializer_class = ReservationEventSeatListSerializer
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

    def validate_reservation(self, value):
        if value.status in [
            Reservation.Status.INVALIDATED,
            Reservation.Status.RESERVED,
            Reservation.Status.CANCELLED,
        ]:
            raise serializers.ValidationError(
                _("reservation is either invalidate. reserved or cancelled")
            )
        return value

    def validate_event_seat(self, value):
        if value.is_occupied():
            raise serializers.ValidationError(_("Seat is already reserved."))
        return value
