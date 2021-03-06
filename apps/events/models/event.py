from django.contrib.auth.models import User
from django.contrib.postgres.functions import TransactionNow
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField

from apps.core.models import BaseModel
from apps.events.managers import EventManager
from apps.events.models import EventTag
from apps.venues.models import Venue


class Event(BaseModel):
    class Status(models.IntegerChoices):
        CREATED = 1, "Created"
        RUNNING = 2, "Running"
        COMPLETED = 3, "Completed"
        COMPLETED_WITH_ERROR = 4, "Completed with error"

    name = models.CharField(max_length=256)
    slug = AutoSlugField(populate_from=["name"])
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_events")
    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE, related_name="venue_events"
    )
    tags = models.ManyToManyField(EventTag, blank=True, related_name="tag_events")
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    objects = EventManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(start_date__lt=F("end_date"), start_date__gt=TransactionNow()),
                name="%(app_label)s_%(class)s_start_date_is_lt_end_date_and_now",
            )
        ]

    def __str__(self):
        return self.name

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        if self.user == request.user:
            return True
        return False

    def get_event_seats(self):
        from apps.events.models import EventSeat

        event = self
        return EventSeat.objects.select_related("event_seat_type__event").filter(
            event_seat_type__event=event
        )

    def get_reserved_event_seats(self):
        from apps.reservations.models import Reservation, ReservationEventSeat

        event = self
        reserved_event_seats_of_a_event = [
            reservation_event_seat.event_seat
            for reservation_event_seat in ReservationEventSeat.objects.select_related(
                "event_seat__event_seat_type",
            ).filter(
                reservation__status=Reservation.Status.RESERVED,
                reservation__event=event,
            )
        ]

        return reserved_event_seats_of_a_event

    def is_eligible_for_reservation(self):
        event = self
        if event.status == Event.Status.COMPLETED:
            return False, _("Event is complete")

        elif event.status == Event.Status.COMPLETED_WITH_ERROR:
            return False, _("Event has completed with errors")

        elif len(event.get_event_seats()) == len(event.get_reserved_event_seats()):
            return False, _("Event is houseful")

        return True, _("Ready for reservation")
