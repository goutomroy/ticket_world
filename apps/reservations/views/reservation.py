from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer


class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("event", "user", "status", "created")

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return (
                super()
                .get_queryset()
                .select_related("user", "event")
                .filter(Q(user=self.request.user) | Q(event__user=self.request.user))
            )
        elif self.action == "destroy":
            return (
                super()
                .get_queryset()
                .select_related("user", "event")
                .filter(
                    Q(user=self.request.user) & ~Q(status=Reservation.Status.RESERVED)
                )
            )
        else:
            return super().get_queryset().select_related("user", "event").all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, url_path="statuses", permission_classes=(IsAuthenticated,))
    def reservation_statuses(self, request):
        data = [{label: value} for value, label in Reservation.Status.choices]
        return Response(data)

