from django.contrib import admin

from apps.events.models import Event, EventSeat, EventSeatType, EventTag


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "venue", "name", "status", "start_date", "end_date"]
    readonly_fields = ["id"]


@admin.register(EventSeatType)
class EventSeatTypeAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "info")
    ordering = ("event", "name")


@admin.register(EventSeat)
class EventSeatAdmin(admin.ModelAdmin):
    list_display = ("event_seat_type", "seat_number")
    ordering = ("seat_number", "event_seat_type")
    list_filter = ("event_seat_type__event", "seat_number")
