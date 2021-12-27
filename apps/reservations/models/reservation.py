import datetime
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.events.models import Event


class Reservation(BaseModel):
    class Status(models.IntegerChoices):
        # reservation status will be changed by background code, not by any http actions
        CREATED = 1, "Created"
        INVALIDATED = 2, "Invalidated"
        RESERVED = 4, "Reserved"

    valid_for_seconds = 15 * 60
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)
    payment_id = models.CharField(max_length=256, null=True, blank=True)
    ticket_number = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)

    class Meta:
        default_related_name = "reservations"

    def __str__(self):
        return f"{self.event.name} | {self.user.username}"

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        if self.user == request.user or self.event.user == request.user:
            return True
        return False

    def has_object_write_permission(self, request):
        if self.user == request.user or self.event.user == request.user:
            return True
        return False

    @property
    def time_elapsed_since_create(self) -> int:
        return int((datetime.datetime.now(timezone.utc) - self.created).total_seconds())

    def is_valid(self):
        reservation = self
        if reservation.status == Event.Status.INVALIDATED:
            return False, _("Reservation is invalidated")

        elif reservation.status == Event.Status.RESERVED:
            return False, _("Reservation is reserved already")

        return True, _("Valid")

    def get_summary(self) -> dict:
        reservation = self
        event_seats = reservation.event_seats.values("event_seat")
        number_of_seats_of_a_reservation = len(event_seats)
        seat_numbers_of_a_reservation = [
            event_seat.seat_number for event_seat in event_seats
        ]
        total_cost_of_a_reservation = 0
        for event_seat in event_seats:
            total_cost_of_a_reservation += event_seat.event_seat_type.price

        data = {
            "event_name": reservation.event.name,
            "reservation_id": reservation.id,
            "ticket_number": reservation.ticket_number,
            "number_of_seats": number_of_seats_of_a_reservation,
            "total_cost": total_cost_of_a_reservation,
            "seat_numbers": seat_numbers_of_a_reservation,
        }
        return data
