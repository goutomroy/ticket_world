from django.contrib.gis.db.models import PointField
from django.db import models

from apps.core.models import BaseModel


class Venue(BaseModel):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=300)
    location = PointField()

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False

    def __str__(self):
        return self.name
