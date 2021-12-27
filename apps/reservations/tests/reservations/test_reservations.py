import json

from django.contrib.auth.models import User
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.events.models import Event, EventSeat, EventTag
from apps.reservations.models import ReservationEventSeat, Reservation
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        for event_seat_type in event.event_seat_types.all():
            for _ in range(1):
                event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
                reservation = baker.make(
                    Reservation, event=event, status=Reservation.Status.RESERVED
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        reservation_ids = []
        for event_seat_type in event.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation, event=event, status=Reservation.Status.RESERVED
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event_1.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_1.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation,
                event=event_1,
                status=Reservation.Status.RESERVED,
                user=self._user_one,
            )
            reservation_ids.append(str(reservation.id))
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
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
            start_date=timezone.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=timezone.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event_1.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_1.event_seat_types.all():
            event_seat = EventSeat.objects.create(event_seat_type=event_seat_type)
            reservation = baker.make(
                Reservation, event=event_1, status=Reservation.Status.RESERVED
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
