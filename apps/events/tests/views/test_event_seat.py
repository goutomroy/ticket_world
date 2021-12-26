import datetime
import json

import pytz
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.events.models import Event, EventSeat, EventTag
from apps.venues.models import Venue


class EventSeatAPITestCase(APITestCase):
    EVENT_SEATS_LIST_PATH = reverse("events:eventseat-list")

    def setUp(self) -> None:
        self._create_api_client_users()

    def _create_api_client_users(self):
        self._user_admin = baker.make(User, is_superuser=True, is_staff=True)
        self._user_staff = baker.make(User, is_staff=True)
        self._user_general = baker.make(User)

        self._client_admin = APIClient()
        self._client_admin.force_authenticate(self._user_admin)

        self._client_staff = APIClient()
        self._client_staff.force_authenticate(self._user_staff)

        self._client_general = APIClient()
        self._client_general.force_authenticate(self._user_general)

    def test_get_all_seats_of_a_event(self):
        event_1 = Event.objects.create(
            name="Happy New Year",
            user=self._user_admin,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        )
        event_1.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_1.event_seat_types.all():
            for _ in range(5):
                EventSeat.objects.create(event_seat_type=event_seat_type)

        event_2 = Event.objects.create(
            name="Chrismas",
            user=self._user_admin,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        )
        event_2.tags.add(*baker.make(EventTag, _quantity=3))

        for event_seat_type in event_2.event_seat_types.all():
            for _ in range(5):
                EventSeat.objects.create(event_seat_type=event_seat_type)

        response = self._client_general.get(
            self.EVENT_SEATS_LIST_PATH, {"event_seat_type__event": event_1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), 15)
