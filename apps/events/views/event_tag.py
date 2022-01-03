from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.events.models import EventTag
from apps.events.serializers import EventTagSerializer


class EventTagViewSet(ModelViewSet):
    queryset = EventTag.objects.all()
    serializer_class = EventTagSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filterset_fields = ["name", "slug"]
