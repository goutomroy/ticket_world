from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin
from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer
from apps.workers.tasks import make_refund


class ReservationPaymentSuccessfulView(ReservationRelatedViewMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = self.request.data.get("payment_id", None)
        if payment_id is None:
            return Response(
                {"payment_id": ["This field is required"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation = self._reservation

        event_result, event_message = reservation.event.is_eligible_for_reservation()
        reservation_result, reservation_message = reservation.is_valid()

        error_message = None
        if event_result is False:
            error_message = event_message + " You will be refunded soon."

        elif reservation_result is False:
            error_message = reservation_message + " You will be refunded soon."

        if error_message:
            make_refund.apply_async(payment_id)
            return Response(
                {"detail": error_message}, status=status.HTTP_400_BAD_REQUEST
            )

        #  here your are really ready to reserve selected seats
        with transaction.atomic():
            Reservation.objects.select_for_update().filter(
                id=reservation, status=Reservation.Status.CREATED
            ).update(status=Reservation.Status.RESERVED, payment_id=payment_id)

            return Response(
                ReservationSerializer(
                    reservation.refresh_from_db(fields=["status", "payment_id"]),
                    context=self.get_serializer_context(),
                ).data
            )
