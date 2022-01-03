from datetime import datetime

import pytz
from celery import shared_task
from django.db import transaction
from django.db.models import Q

from apps.events.models import Event
from apps.reservations.models import Reservation


@shared_task
def event_starter():
    with transaction.atomic():
        events = Event.objects.filter(
            status=Event.Status.CREATED, start_date__gte=datetime.now(tz=pytz.UTC)
        )
        objects = []
        for event in events:
            event.status = Event.Status.RUNNING
            objects.append(event)
        Event.objects.bulk_update(objects, fields=["status"])


@shared_task
def event_stopper():
    with transaction.atomic():
        events = Event.objects.filter(
            status=Event.Status.RUNNING, end_date__gte=datetime.now(tz=pytz.UTC)
        )
        objects = []
        for event in events:
            event.status = Event.Status.COMPLETED
            objects.append(event)
        Event.objects.bulk_update(objects, fields=["status"])


@shared_task
def start_reservation_invalidator():
    with transaction.atomic():
        objects = []
        reservations = Reservation.objects.filter(Q(status=Reservation.Status.CREATED))
        for reservation in reservations:
            if reservation.time_elapsed_since_create() > Reservation.valid_for_seconds:
                reservation.status = Reservation.Status.INVALIDATED
                objects.append(reservation)

        Reservation.objects.bulk_update(objects, fields=["status"])


@shared_task
def make_refund(payment_id):
    with transaction.atomic():
        pass
