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
        qs = Event.objects.select_for_update().filter(
            status=Event.Status.CREATED, start_date__gte=datetime.now(tz=pytz.UTC)
        )
        list(qs)
        qs.update(status=Event.Status.RUNNING)


@shared_task
def event_stopper():
    with transaction.atomic():
        qs = Event.objects.select_for_update().filter(
            status=Event.Status.RUNNING, end_date__gte=datetime.now(tz=pytz.UTC)
        )
        list(qs)
        qs.update(status=Event.Status.COMPLETED)


@shared_task
def start_reservation_invalidator():
    # TODO : need to improved this task
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
