import uuid

from django.db import models


class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        #: Don't create table in database for this model.
        abstract = True
