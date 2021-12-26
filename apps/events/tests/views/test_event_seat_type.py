import datetime
import json

from django.contrib.auth.models import User
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.events.models import Event, EventSeatType, EventTag
from apps.venues.models import Venue


class EventSeatTypeAPITestCase(APITestCase):
    EVENT_SEAT_TYPE_LIST_PATH = reverse("events:eventseattype-list")

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

    def test_get_all_event_seat_types_of_a_event(self):
        event = Event.objects.create(
            user=self._user_admin,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))

        response = self._client_general.get(
            self.EVENT_SEAT_TYPE_LIST_PATH, {"event": event.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content)), 3)

    def test_only_creator_of_event_can_create_event_seat_types_for_a_event(
        self,
    ):
        event = Event.objects.create(
            user=self._user_admin,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        response = self._client_general.post(
            self.EVENT_SEAT_TYPE_LIST_PATH,
            {"event": event.id, "price": 35, "name": "child friendly"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_creator_can_update_event_seat_type(self):
        event = Event.objects.create(
            user=self._user_admin,
            status=Event.Status.RUNNING,
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=timezone.utc),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=timezone.utc),
        )
        event.tags.add(*baker.make(EventTag, _quantity=3))
        event_seat_type = EventSeatType.objects.filter(event=event.id).first()
        url = reverse("events:eventseattype-detail", kwargs={"pk": event_seat_type.id})

        response = self._client_general.patch(url, {"name": "for kids"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self._client_staff.patch(url, {"name": "for kids"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self._client_admin.patch(url, {"name": "for kids"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
