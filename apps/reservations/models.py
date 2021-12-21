import datetime
import uuid
from typing import List

from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone

from apps.core.models import BaseModel
from apps.events.models import Event, EventSeat


class Reservation(BaseModel):
    class Status(models.IntegerChoices):
        CREATED = 1, "Created"
        INVALIDATED = 2, "Invalidated"
        CANCELLED = 3, "Cancelled"
        RESERVED = 4, "Reserved"

    valid_for_seconds = 15 * 60
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)
    payment_id = models.CharField(max_length=256, null=True, blank=True)
    ticket_number = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)

    @property
    def time_elapsed_since_create(self):
        return int((datetime.datetime.now(timezone.utc) - self.created).total_seconds())

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_ticket_permission(request):
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

    def __str__(self):
        return f"{self.event.name} | {self.user.username}"


class ReservationEventSeat(BaseModel):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    event_seat = models.ForeignKey(EventSeat, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["reservation", "event_seat"],
                name="unique_reservation_event_seat",
            )
        ]

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.reservation.user == request.user
            or self.reservation.event.user == request.user
        ):
            return True
        return False

    def has_object_write_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.reservation.user == request.user
            or self.reservation.event.user == request.user
        ):
            return True
        return False

    def event_seats(self) -> List[EventSeat]:
        return [each.event_seat for each in self.objects.filter(reservation=self)]

    def __str__(self):
        return f"{self.reservation} | {self.event_seat}"
