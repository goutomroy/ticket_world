from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import AutoSlugField
from ordered_model.models import OrderedModelBase

from apps.core.models import BaseModel
from apps.events.managers import EventManager
from apps.venues.models import Venue


class EventTag(BaseModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from=["name"])

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

    def __str__(self):
        return self.name


class Event(BaseModel):
    class Status(models.IntegerChoices):
        CREATED = 1, "Created"
        RUNNING = 2, "Running"
        COMPLETED = 3, "Completed"
        COMPLETED_WITH_ERROR = 4, "Completed with error"

    name = models.CharField(max_length=256)
    slug = AutoSlugField(populate_from=["name"])
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    tags = models.ManyToManyField(EventTag, blank=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.CREATED)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    objects = EventManager()

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.user == request.user
        ):
            return True
        return False

    def get_reserved_event_seats(self):
        from apps.reservations.models import Reservation, ReservationEventSeat

        event = self
        reserved_event_seats_of_a_event = [
            each.event_seat
            for each in ReservationEventSeat.objects.filter(
                reservation__status=Reservation.Status.RESERVED,
                reservation__event=event,
            )
        ]
        return reserved_event_seats_of_a_event

    def __str__(self):
        return self.name


class EventSeatType(BaseModel):

    DEFAULT_SEAT_TYPES = [
        {"name": "general", "info": "GENERAL", "price": 10},
        {"name": "vip", "info": "VIP", "price": 30},
        {"name": "vvip", "info": "VVIP", "price": 60},
    ]

    name = models.CharField(max_length=100)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="seat_types"
    )
    price = models.PositiveIntegerField(default=0)
    info = models.CharField(max_length=150, blank=True)

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        if (
            request.user.is_superuser
            or request.user.is_staff
            or self.event.user == request.user
        ):
            return True
        return False

    def __str__(self):
        return f"{self.event.name} | {self.name}"


class EventSeat(BaseModel, OrderedModelBase):

    event_seat_type = models.ForeignKey(EventSeatType, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField(editable=False, db_index=True)

    order_field_name = "seat_number"
    order_with_respect_to = "event_seat_type__event"

    class Meta:
        ordering = ("seat_number",)

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

    def is_occupied(self):
        from apps.reservations.models import Reservation, ReservationEventSeat

        if ReservationEventSeat.objects.filter(
            reservation__status=Reservation.Status.RESERVED, event_seat=self
        ).exists():
            return True
        return False

    def __str__(self):
        return f"{self.event_seat_type} | {self.seat_number}"
