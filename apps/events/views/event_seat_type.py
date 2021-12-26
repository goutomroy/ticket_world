from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.events.models import EventSeatType
from apps.events.serializers import EventSeatTypeSerializer


class EventSeatTypeViewSet(ModelViewSet):
    queryset = EventSeatType.objects.all()
    serializer_class = EventSeatTypeSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("event",)

    def get_queryset(self):
        return super().get_queryset().select_related("event").all()
