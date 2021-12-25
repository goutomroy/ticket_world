from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.events.models import Event, EventSeat, EventSeatType, EventTag
from apps.events.serializers import (
    EventSeatSerializer,
    EventSeatTypeSerializer,
    EventSerializer,
    EventTagSerializer,
)


class EventTagViewSet(ModelViewSet):
    queryset = EventTag.objects.all()
    serializer_class = EventTagSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("user", "status", "start_date", "end_date")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("tags")
            .filter(status=Event.Status.RUNNING)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, url_path="statuses", permission_classes=(IsAuthenticated,))
    def event_statuses(self, request):
        data = [{label: value} for value, label in Event.Status.choices]
        return Response(data)

    @action(detail=True, methods=["get"], permission_classes=(IsAuthenticated,))
    def reserved_seats(self, request, pk=None):
        event = self.get_object()
        reserved_event_seats_of_a_event = event.get_reserved_event_seats()
        return Response(
            EventSeatSerializer(
                reserved_event_seats_of_a_event,
                many=True,
                context=self.get_serializer_context(),
            ).data
        )


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


class EventSeatViewSet(ModelViewSet):
    queryset = EventSeat.objects.all()
    serializer_class = EventSeatSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("event_seat_type", "event_seat_type__event")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("event_seat_type", "event_seat_type__event")
            .all()
        )

    # TODO: before deleting check whether its accupied or not
