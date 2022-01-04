from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.events.models import Event
from apps.reservations.models import Reservation


@shared_task
def event_starter():
    with transaction.atomic():
        qs = Event.objects.select_for_update().filter(
            status=Event.Status.CREATED, start_date__gte=timezone.now()
        )
        list(qs)
        qs.update(status=Event.Status.RUNNING)


@shared_task
def event_stopper():
    with transaction.atomic():
        qs = Event.objects.select_for_update().filter(
            status=Event.Status.RUNNING, end_date__gte=timezone.now()
        )
        list(qs)
        qs.update(status=Event.Status.COMPLETED)


@shared_task
def start_reservation_invalidator():
    with transaction.atomic():
        qs = Reservation.objects.select_for_update().filter(
            status=Reservation.Status.CREATED,
            created_lte=timezone.now()
            - timedelta(seconds=Reservation.valid_for_seconds),
        )
        list(qs)
        qs.update(status=Reservation.Status.INVALIDATED)


@shared_task
def make_refund(payment_id):
    with transaction.atomic():
        pass
