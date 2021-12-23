from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer
from apps.workers.tasks import make_refund


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

    @action(
        detail=True,
        methods=["post"],
        permission_classes=(IsAuthenticated, DRYPermissions),
    )
    def payment_successful(self, request, pk=None):
        payment_id = self.request.data.get("payment_id", None)
        if payment_id is None:
            return Response(
                {"payment_id": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation = super().get_object()
        result, message = reservation.event.is_eligible_for_reservation()
        error_message = None

        if result is False:
            error_message = message + " You will be refunded soon."
        elif reservation.status == Reservation.Status.INVALIDATED:
            error_message = _(
                "reservation is already invalidated. You will be refunded soon"
            )
        elif reservation.status == Reservation.Status.RESERVED:
            error_message = _(
                "you already paid for this reservation. You will be refunded soon"
            )

        if error_message:
            make_refund.apply_async(payment_id)
            return Response(
                {"detail": error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        #  here your are really ready to reserve selected seats
        Reservation.objects.select_for_update().filter(
            id=reservation, status=Reservation.Status.CREATED
        ).update(status=Reservation.Status.RESERVED, payment_id=payment_id)

        ticket_url = reverse("reservations:reservation-ticket", kwargs={"pk": pk})
        return redirect(ticket_url)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=(IsAuthenticated, DRYPermissions),
    )
    def ticket(self, request, pk):
        reservation = super().get_object()
        if reservation.status != Reservation.Status.RESERVED:
            return Response(
                {"detail : reservation wasn't successful"}, status.HTTP_400_BAD_REQUEST
            )

        data = reservation.get_summary()
        return Response(data, status=status.HTTP_200_OK)
