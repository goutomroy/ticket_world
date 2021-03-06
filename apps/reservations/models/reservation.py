import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.events.models import Event


class Reservation(BaseModel):
    class Status(models.IntegerChoices):
        # reservation status will be changed by background code, not by any http actions
        CREATED = 1, "Created"
        INVALIDATED = 2, "Invalidated"
        PAYMENT_STARTED = 3, "Payment Started"
        PAYMENT_COMPLETE = 4, "Payment Complete"
        RESERVED = 5, "Reserved"

    valid_for_seconds = 15 * 60
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)
    payment_id = models.CharField(max_length=256, null=True, blank=True)
    ticket_number = models.UUIDField(editable=False, default=uuid.uuid4, unique=True)

    class Meta:
        default_related_name = "reservations"
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_completed_payment_must_have_payment_id",
                check=(
                    Q(
                        status__in=[1, 2, 3],
                        payment_id__isnull=True,
                    )
                    | Q(
                        status__in=[4, 5],
                        payment_id__isnull=False,
                    )
                ),
            )
        ]

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

    def is_valid(self):

        from apps.reservations.models import ReservationEventSeat

        reservation = self
        if reservation.status == Reservation.Status.INVALIDATED:
            return False, {"status": _("Reservation is invalidated.")}

        elif reservation.status == Reservation.Status.RESERVED:
            return False, {"status": _("Reservation is reserved already.")}

        # find event seats in a reservation that is already reserved
        # by other reservation
        reservation_event_seat_ids = ReservationEventSeat.objects.filter(
            reservation=reservation
        ).values_list("event_seat_id", flat=True)

        event_seat_ids = (
            ReservationEventSeat.objects.select_related("reservation")
            .filter(
                ~Q(reservation=reservation)
                & Q(reservation__status__gte=Reservation.Status.PAYMENT_COMPLETE)
                & Q(event_seat__in=list(reservation_event_seat_ids)),
            )
            .values_list("event_seat_id", flat=True)
        )

        # event_seat_ids = []
        # for reservation_event_seat in reservation.event_seats.all():
        #     if reservation_event_seat.event_seat.is_reserved():
        #         event_seat_ids.append(reservation_event_seat.event_seat.id)

        if event_seat_ids:
            return False, {
                "reserved_seats": event_seat_ids,
                "message": _("You selected already reserved seats."),
            }

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
