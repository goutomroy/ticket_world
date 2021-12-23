from django.db import models
from ordered_model.models import OrderedModelBase

from apps.core.models import BaseModel
from apps.events.models import EventSeatType


class EventSeat(BaseModel, OrderedModelBase):

    event_seat_type = models.ForeignKey(EventSeatType, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField(editable=False, db_index=True)

    order_field_name = "seat_number"
    order_with_respect_to = "event_seat_type__event"

    class Meta:
        ordering = ("seat_number",)

    def __str__(self):
        return f"{self.event_seat_type} | {self.seat_number}"

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    def has_object_put_permission(self, request):
        return False

    def has_object_patch_permission(self, request):
        return False

    def is_reserved(self) -> bool:
        from apps.reservations.models import Reservation, ReservationEventSeat

        event_seat = self
        if ReservationEventSeat.objects.filter(
            reservation__status=Reservation.Status.RESERVED, event_seat=event_seat
        ).exists():
            return True
        return False
