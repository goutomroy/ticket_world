from django.contrib import admin

from apps.events.models import EventTag, Event
from apps.events.models import EventSeatType, EventSeat


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "venue", "name", "status"]


@admin.register(EventSeatType)
class EventSeatTypeAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "info")
    ordering = ("event", "name")


@admin.register(EventSeat)
class EventSeatAdmin(admin.ModelAdmin):
    list_display = ("event_seat_type", "seat_number")
    ordering = ("event_seat_type", "seat_number")