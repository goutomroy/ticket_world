from django.contrib import admin

from apps.reservations.models import Reservation, ReservationEventSeat


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["user", "event", "status", "payment_id", "ticket_number"]


@admin.register(ReservationEventSeat)
class ReservationEventSeatAdmin(admin.ModelAdmin):
    list_display = ["reservation", "event_seat"]
