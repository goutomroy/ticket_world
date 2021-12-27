from django.contrib import admin

from apps.reservations.models import Reservation, ReservationEventSeat


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "event", "status", "payment_id", "ticket_number"]
    readonly_fields = ["id"]


@admin.register(ReservationEventSeat)
class ReservationEventSeatAdmin(admin.ModelAdmin):
    list_display = ["id", "reservation", "event_seat"]
    readonly_fields = ["id"]
