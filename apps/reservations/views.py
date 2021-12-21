from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.reservations.models import Reservation, ReservationEventSeat
from apps.reservations.serializers import (
    ReservationEventSeatSerializer,
    ReservationSerializer,
)


class ReservationViewSet(ModelViewSet):

    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("event", "user", "status")

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return super().get_queryset().select_related("user", "event").all()

        return (
            super()
            .get_queryset()
            .select_related("user", "event")
            .filter(Q(user=self.request.user) | Q(event__user=self.request.user))
        )

    @action(detail=False, url_path="statuses", permission_classes=(IsAuthenticated,))
    def reservation_statuses(self, request):
        data = [{label: value} for value, label in Reservation.Status.choices]
        return Response(data)

    @action(detail=True, methods=["get"], permission_classes=(IsAuthenticated,))
    def payment_successful(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status in [
            Reservation.Status.INVALIDATED,
            Reservation.Status.CANCELLED,
        ]:
            return Response(
                {"detail": "reservation cancelled or invalidated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Reservation.objects.select_for_update().filter(
            id=reservation, status=Reservation.Status.CREATED
        ).update(status=Reservation.Status.RESERVED)

        return Response(
            ReservationSerializer(
                reservation.refresh_from_db(fields=["status"]),
                many=True,
                context=self.get_serializer_context(),
            ).data
        )


class ReservationVenueSeatViewSet(ModelViewSet):
    queryset = ReservationEventSeat.objects.all()
    serializer_class = ReservationEventSeatSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "reservation__event",
        "reservation__status",
        "reservation__payment_id",
    )
    ordering = ("reservation__event", "reservation__status", "reservation__payment_id")

    def get_queryset(self):
        return ReservationEventSeat.objects.select_related(
            "reservation", "event_seat"
        ).filter(reservation__user_id=self.request.user)

    def get_serializer(self, *args, **kwargs):
        if self.action == "create" and isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
            kwargs["allow_empty"] = False
        return super().get_serializer(*args, **kwargs)
