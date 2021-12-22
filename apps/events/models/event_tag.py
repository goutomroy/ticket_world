from django.db import models
from django_extensions.db.fields import AutoSlugField

from apps.core.models import BaseModel


class EventTag(BaseModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from=["name"])

    def __str__(self):
        return self.name

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True
