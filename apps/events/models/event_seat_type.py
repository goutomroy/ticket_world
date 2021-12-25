from django.db import models

from apps.core.models import BaseModel
from apps.events.models import Event


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

    def __str__(self):
        return f"{self.event.name} | {self.name}"

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        if self.event.user == request.user:
            return True
        return False
