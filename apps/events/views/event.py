from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from apps.events.models import Event
from apps.events.serializers import EventSeatSerializer, EventSerializer


class EventViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("user", "venue", "status", "start_date", "end_date")

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user", "venue")
            .prefetch_related("tags")
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
