from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.events.models import EventSeat
from apps.events.serializers import EventSeatSerializer


class EventSeatViewSet(ModelViewSet):
    queryset = EventSeat.objects.all()
    serializer_class = EventSeatSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filterset_fields = ("event_seat_type", "event_seat_type__event")

    def get_queryset(self):
        return super().get_queryset().select_related("event_seat_type__event").all()

    # TODO: before deleting check whether its occupied or not
