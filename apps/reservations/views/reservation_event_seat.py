from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.reservations.models import ReservationEventSeat
from apps.reservations.serializers import ReservationEventSeatSerializer


class ReservationEventSeatViewSet(ModelViewSet):
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
