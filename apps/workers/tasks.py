from datetime import datetime

import pytz
from celery import shared_task

from apps.events.models import Event
from apps.reservations.models import Reservation


@shared_task
def event_starter():
    events = Event.objects.filter(status=Event.Status.CREATED, start_date__gte=datetime.now(tz=pytz.UTC))
    objects = []
    for event in events:
        event.status = Event.Status.RUNNING
        objects.append(event)
    Event.objects.bulk_update(objects, fields=["status"])
    

@shared_task
def event_stopper():
    events = Event.objects.filter(status=Event.Status.RUNNING, end_date__gte=datetime.now(tz=pytz.UTC))
    objects = []
    for event in events:
        event.status = Event.Status.COMPLETED
        objects.append(event)
    Event.objects.bulk_update(objects, fields=["status"])


@shared_task
def start_reservation_invalidator():
    objects = []
    reservations = Reservation.objects.filter(status=Reservation.Status.CREATED)
    # TODO: use annotation here
    for reservation in reservations:
        if reservation.time_elapsed_since_create() > Reservation.valid_for_seconds:
            reservation.status = Reservation.Status.INVALIDATED
            objects.append(reservation)

    Reservation.objects.bulk_update(objects, fields=["status"])

