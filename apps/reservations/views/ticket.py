from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mixins import ReservationRelatedViewMixin
from apps.reservations.models import Reservation


class ReservationTicketView(ReservationRelatedViewMixin, APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if self._reservation.status != Reservation.Status.RESERVED:
            return Response(
                {"detail : reservation wasn't successful"}, status.HTTP_400_BAD_REQUEST
            )

        data = self._reservation.get_summary()
        return Response(data)
