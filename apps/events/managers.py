from django.db import models, transaction


class EventManager(models.Manager):

    @transaction.atomic
    def create(self, **kwargs):
        event = super().create(**kwargs)
        self._create_default_event_seat_types(event)
        return event

    @transaction.atomic
    def _create_default_event_seat_types(self, event):
        from apps.events.models import EventSeatType
        event_seat_types = [EventSeatType(event=event, name=seat_type["name"], price=seat_type["price"])
                            for seat_type in EventSeatType.DEFAULT_SEAT_TYPES]
        EventSeatType.objects.bulk_create(event_seat_types)
