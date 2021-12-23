from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.reservations.models import Reservation, ReservationEventSeat
from apps.reservations.serializers import ReservationEventSeatSerializer


class ReservationEventSeatViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = ReservationEventSeat.objects.all()
    serializer_class = ReservationEventSeatSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "reservation",
        "reservation__event",
        "reservation__status",
    )
    ordering = (
        "reservation__event",
        "reservation__status",
    )

    def get_queryset(self):

        if self.action in ["list", "retrieve"]:
            return ReservationEventSeat.objects.select_related(
                "reservation", "event_seat"
            ).filter(
                Q(reservation__user=self.request.user)
                | Q(reservation__event__user=self.request.user)
            )

        elif self.action == "destroy":
            return ReservationEventSeat.objects.select_related(
                "reservation", "event_seat"
            ).filter(
                reservation__user=self.request.user,
                reservation__status=Reservation.Status.CREATED,
            )

        else:
            return ReservationEventSeat.objects.select_related(
                "reservation", "event_seat"
            ).filter(reservation__user=self.request.user)
