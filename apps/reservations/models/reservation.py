import datetime
import uuid
from typing import List

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.events.models import Event, EventSeat


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

    def __str__(self):
        return f"{self.event.name} | {self.user.username}"

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_ticket_permission(request):
        return True

    @staticmethod
    def has_payment_successful_permission(request):
        return True

    def has_object_read_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.user == request.user
            or self.event.user == request.user
        ):
            return True
        return False

    def has_object_write_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.user == request.user
            or self.event.user == request.user
        ):
            return True
        return False

    def has_object_ticket_permission(self, request):
        return request.user == self.user

    def has_object_payment_successful_permission(self, request):
        return request.user == self.user

    @property
    def event_seats(self) -> List[EventSeat]:

        from apps.reservations.models import ReservationEventSeat

        return [
            each.event_seat
            for each in ReservationEventSeat.objects.select_related(
                "event_seat"
            ).filter(reservation=self.id)
        ]

    @property
    def time_elapsed_since_create(self) -> int:
        return int((datetime.datetime.now(timezone.utc) - self.created).total_seconds())

    def get_summary(self) -> dict:
        reservation = self
        event_seats = reservation.event_seats
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
