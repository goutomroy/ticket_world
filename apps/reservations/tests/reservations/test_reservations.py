import datetime
import json
from unittest.mock import patch

import pytz
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.events.models import Event, EventSeat, EventTag
from apps.reservations.models import Reservation, ReservationEventSeat
from apps.venues.models import Venue


class ReservationAPITestCase(APITestCase):
    RESERVATIONS_LIST_PATH = reverse("reservations:reservation-list")

    def setUp(self) -> None:
        self._user_one, self._client_one = self._create_user_and_api_client_user()
        self._user_two, self._client_two = self._create_user_and_api_client_user()
        self._user_three, self._client_three = self._create_user_and_api_client_user()

    def _create_user_and_api_client_user(self):
        user = baker.make(User)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def test_reservation_create_successful(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        for event_seat_type in event.event_seat_types.all():
            for _ in range(5):
                EventSeat.objects.create(event_seat_type=event_seat_type)

        response = self._client_one.post(
            self.RESERVATIONS_LIST_PATH, {"event": str(event.id)}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reservation_cant_be_created_when_event_is_completed(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.COMPLETED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        for event_seat_type in event.event_seat_types.all():
            for _ in range(5):
                EventSeat.objects.create(event_seat_type=event_seat_type)

        response = self._client_one.post(
            self.RESERVATIONS_LIST_PATH, {"event": str(event.id)}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reservation_cant_be_created_when_event_is_houseful(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        for event_seat_type in event.event_seat_types.all():
            for _ in range(1):
                event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
                reservation = baker.make(
                    Reservation,
                    event=event,
                    status=Reservation.Status.RESERVED,
                    payment_id="payment_id",
                )
                baker.make(
                    ReservationEventSeat,
                    reservation=reservation,
                    event_seat=event_seat,
                )

        response = self._client_one.post(
            self.RESERVATIONS_LIST_PATH, {"event": str(event.id)}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_event_creator_can_get_all_reservations_of_an_event(self):
        """
        event creator can get all the reservations of his events,
        plus reservations in other events created by him.
        """
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        reservation_ids = []
        for event_seat_type in event.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation,
                event=event,
                status=Reservation.Status.RESERVED,
                payment_id="payment_id",
                user=self._user_three,
            )
            reservation_ids.append(str(reservation.id))
            baker.make(
                ReservationEventSeat,
                reservation=reservation,
                event_seat=event_seat,
            )

        event_1 = Event.objects.create(
            name="Happy Merry Christmas",
            user=self._user_two,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event_1.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_1.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation,
                event=event_1,
                status=Reservation.Status.RESERVED,
                payment_id="payment_id",
            )
            baker.make(
                ReservationEventSeat,
                reservation=reservation,
                event_seat=event_seat,
            )

        response = self._client_one.get(self.RESERVATIONS_LIST_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_reservation_ids = [each["id"] for each in json.loads(response.content)]
        self.assertListEqual(response_reservation_ids, reservation_ids)

    def test_general_user_can_only_get_his_reservations(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        reservation_ids = []
        for event_seat_type in event.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation,
                event=event,
                user=self._user_three,
                status=Reservation.Status.RESERVED,
                payment_id="payment_id",
            )
            reservation_ids.append(str(reservation.id))
            baker.make(
                ReservationEventSeat,
                reservation=reservation,
                event_seat=event_seat,
            )

        event_1 = Event.objects.create(
            name="Happy Merry Christmas",
            user=self._user_two,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event_1.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_1.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation,
                event=event_1,
                status=Reservation.Status.RESERVED,
                payment_id="payment_id",
            )
            baker.make(
                ReservationEventSeat,
                reservation=reservation,
                event_seat=event_seat,
            )

        response = self._client_three.get(self.RESERVATIONS_LIST_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_reservation_ids = [each["id"] for each in json.loads(response.content)]
        self.assertListEqual(response_reservation_ids, reservation_ids)

    def test_general_user_can_delete_his_not_reserved_reservation(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = baker.make(
            EventSeat, event_seat_type=event.event_seat_types.first()
        )
        reservation = baker.make(
            Reservation,
            event=event,
            user=self._user_three,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation,
            event_seat=event_seat,
        )

        response = self._client_three.delete(
            reverse(
                "reservations:reservation-detail", kwargs={"pk": str(reservation.id)}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_general_user_cant_delete_his_reserved_reservation(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = baker.make(
            EventSeat, event_seat_type=event.event_seat_types.first()
        )
        reservation = baker.make(
            Reservation,
            event=event,
            user=self._user_three,
            status=Reservation.Status.RESERVED,
            payment_id="payment_id",
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation,
            event_seat=event_seat,
        )

        response = self._client_three.delete(
            reverse(
                "reservations:reservation-detail", kwargs={"pk": str(reservation.id)}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_reservation_is_not_allowed(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = baker.make(
            EventSeat, event_seat_type=event.event_seat_types.first()
        )
        reservation = baker.make(
            Reservation,
            event=event,
            user=self._user_three,
            status=Reservation.Status.RESERVED,
            payment_id="payment_id",
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation,
            event_seat=event_seat,
        )

        response = self._client_three.patch(
            reverse(
                "reservations:reservation-detail", kwargs={"pk": str(reservation.id)}
            ),
            {"user": str(self._user_two.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_final_reservation_validation_successful(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )
        event_seat_1 = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )

        reservation_user_one = baker.make(
            Reservation,
            event=event,
            user=self._user_one,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat_1,
        )

        reservation_user_two = baker.make(
            Reservation,
            event=event,
            user=self._user_two,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_two,
            event_seat=event_seat,
        )

        response = self._client_one.get(
            reverse(
                "reservations:reservation-final-validation",
                kwargs={"reservation_id": str(reservation_user_one.id)},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_final_reservation_validation_fails_when_number_of_seats_are_odd(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )

        reservation_user_one = baker.make(
            Reservation,
            event=event,
            user=self._user_one,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat,
        )

        reservation_user_two = baker.make(
            Reservation,
            event=event,
            user=self._user_two,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_two,
            event_seat=event_seat,
        )

        response = self._client_one.get(
            reverse(
                "reservations:reservation-final-validation",
                kwargs={"reservation_id": str(reservation_user_one.id)},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_final_reservation_validation_fails_when_all_seats_are_not_around_each_other(  # noqa
        self,
    ):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )
        EventSeat.objects.create(event_seat_type=event.event_seat_types.first())
        event_seat_2 = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )

        reservation_user_one = baker.make(
            Reservation,
            event=event,
            user=self._user_one,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat_2,
        )

        response = self._client_one.get(
            reverse(
                "reservations:reservation-final-validation",
                kwargs={"reservation_id": str(reservation_user_one.id)},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_successful(self):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )
        event_seat_1 = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )

        reservation_user_one = baker.make(
            Reservation,
            event=event,
            user=self._user_one,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat_1,
        )

        reservation_user_two = baker.make(
            Reservation,
            event=event,
            user=self._user_two,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_two,
            event_seat=event_seat,
        )

        response = self._client_one.post(
            reverse(
                "reservations:reservation-payment-successful",
                kwargs={"reservation_id": str(reservation_user_one.id)},
            ),
            data={"payment_id": "f2asd4fa5sd4f45fas5"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("apps.workers.tasks.make_refund.apply_async")
    def test_make_refund(self, make_refund_mock):
        event = Event.objects.create(
            name="Happy New Year",
            user=self._user_one,
            status=Event.Status.CREATED,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        event_seat_1 = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )
        event_seat_2 = EventSeat.objects.create(
            event_seat_type=event.event_seat_types.first()
        )

        reservation_user_one = baker.make(
            Reservation,
            event=event,
            user=self._user_one,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat_1,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_one,
            event_seat=event_seat_2,
        )

        reservation_user_two = baker.make(
            Reservation,
            event=event,
            user=self._user_two,
            status=Reservation.Status.CREATED,
        )
        baker.make(
            ReservationEventSeat,
            reservation=reservation_user_two,
            event_seat=event_seat_1,
        )
        Reservation.objects.filter(id=reservation_user_two.id).update(
            status=Reservation.Status.RESERVED, payment_id="payment_id"
        )

        response = self._client_one.post(
            reverse(
                "reservations:reservation-payment-successful",
                kwargs={"reservation_id": str(reservation_user_one.id)},
            ),
            data={"payment_id": "f2asd4fa5sd4f45fas5"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
