from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin
from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer
from apps.workers.tasks import make_refund


class ReservationPaymentSuccessfulView(ReservationRelatedViewMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = self._validate_and_get_payment_id()
        self._validate_event_for_reservation(payment_id)

        #  here your really ready to reserve the selected seats
        Reservation.objects.select_related("event").select_for_update().filter(
            id=self._reservation.id
        ).update(status=Reservation.Status.RESERVED, payment_id=payment_id)

        return Response(
            ReservationSerializer(
                self._reservation.refresh_from_db(fields=["status", "payment_id"])
            ).data
        )

    def _validate_and_get_payment_id(self):
        payment_id = self.request.data.get("payment_id", None)
        if payment_id is None:
            raise serializers.ValidationError(
                {"payment_id": ["This field is required"]}
            )
        return payment_id

    def _validate_event_for_reservation(self, payment_id):

        (
            event_result,
            event_message,
        ) = self._reservation.event.is_eligible_for_reservation()

        reservation_result, reservation_message = self._reservation.is_valid()

        error_response_data = dict()
        if event_result is False:
            error_response_data["detail"] = event_message + _(
                " You will be refunded soon."
            )

        elif reservation_result is False:
            if "status" in reservation_message:
                error_response_data["detail"] = reservation_message["status"] + _(
                    " You will be refunded soon."
                )
            elif "reserved_seats" in reservation_message:
                error_response_data["detail"] = reservation_message["message"] + _(
                    " You will be refunded soon."
                )
                error_response_data["reserved_seats"] = reservation_message[
                    "reserved_seats"
                ]

        if error_response_data:
            make_refund.apply_async((payment_id,))
            raise serializers.ValidationError(error_response_data)
