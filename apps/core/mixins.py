import uuid

from django.conf import settings
from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from apps.reservations.models import Reservation


class ReservationRelatedViewMixin:
    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)

        requested_reservation_id: uuid = self._get_requested_reservation_id(kwargs)

        if requested_reservation_id and not self._is_requested_reservation_exist(
            requested_reservation_id
        ):
            raise Http404

        return request

    def initial(self, request: Request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        requested_reservation_id: uuid = self._get_requested_reservation_id(kwargs)

        if (
            requested_reservation_id
            and not self._is_requested_reservation_created_by_user(
                requested_reservation_id, request
            )
        ):
            raise PermissionDenied

        self._reservation = self._get_requested_reservation(requested_reservation_id)

    def _get_requested_reservation_id(self, kwargs) -> uuid:
        return kwargs.get(settings.RESERVATION_ID_URL_KEY)

    def _is_requested_reservation_exist(self, requested_reservation_id: uuid) -> bool:
        return Reservation.objects.filter(pk=requested_reservation_id).exists()

    def _is_requested_reservation_created_by_user(
        self, requested_reservation_id: uuid, request: Request
    ) -> bool:
        return Reservation.objects.filter(
            pk=requested_reservation_id, user=request.user
        ).exists()

    def _get_requested_reservation(self, requested_reservation_id: uuid) -> uuid:
        return Reservation.objects.get(pk=requested_reservation_id)
