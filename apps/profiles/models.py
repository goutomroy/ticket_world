from django.contrib.auth.models import User
from django.db import models

from apps.core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    braintree_user_id = models.CharField(max_length=256, unique=True)
    bio = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "braintree_user_id"],
                name="%(app_label)s_%(class)s_unique_user_braintree_user_id",
            )
        ]

    def __str__(self):
        return self.user.username
