from django.db import models
from django.db.models import UniqueConstraint

from apps.core.models import BaseModel
from apps.events.models import EventSeat
from apps.reservations.models import Reservation


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

    def __str__(self):
        return f"{self.reservation} | {self.event_seat}"

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