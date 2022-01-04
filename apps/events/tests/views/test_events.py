import datetime

import pytz
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.events.models import Event, EventTag
from apps.venues.models import Venue


class EventAPITestCase(APITestCase):
    EVENT_LIST_PATH = reverse("events:event-list")

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

    def test_anyone_can_create_event(self):
        data = {
            "name": "New Year Celebration",
            "venue": baker.make(Venue).id,
            "tags": [tag.id for tag in baker.make(EventTag, _quantity=3)],
            "start_date": datetime.datetime(2022, 5, 1, 7, 30, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2022, 5, 5, 7, 30, 30, tzinfo=pytz.UTC),
        }
        response = self._client_admin.post(self.EVENT_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            "name": "New Year Celebration",
            "venue": baker.make(Venue).id,
            "tags": [tag.id for tag in baker.make(EventTag, _quantity=3)],
            "start_date": datetime.datetime(2022, 5, 1, 7, 30, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2022, 5, 5, 7, 30, 30, tzinfo=pytz.UTC),
        }
        response = self._client_general.post(self.EVENT_LIST_PATH, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_anyone_can_get_event_list(self):
        response = self._client_admin.get(self.EVENT_LIST_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_general.get(self.EVENT_LIST_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anyone_can_get_single_event(self):
        event = baker.make(Event, status=Event.Status.RUNNING)
        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})
        response = self._client_admin.get(single_event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_general.get(single_event_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_creator_can_update_event(self):
        event = baker.make(
            Event,
            user=self._user_admin,
            status=Event.Status.RUNNING,
            tags=baker.make(EventTag, _quantity=3),
        )

        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})
        put_data = {
            "name": "New Name",
            "venue": event.venue.id,
            "tags": [tag.id for tag in baker.make(EventTag, _quantity=3)],
            "start_date": datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        }
        response = self._client_admin.put(single_event_url, put_data)
        self.assertEqual(event.tags.count(), 6)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_admin.patch(single_event_url, {"name": "New Name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_creator_cant_update_event(self):
        event = baker.make(Event, user=self._user_admin, status=Event.Status.RUNNING)
        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})

        response = self._client_general.put(
            single_event_url,
            {
                "name": "New Name",
                "venue": event.venue.id,
                "start_date": datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
                "end_date": datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self._client_general.patch(single_event_url, {"name": "New Name"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_creator_can_destroy_event(self):
        event = baker.make(Event, user=self._user_admin, status=Event.Status.RUNNING)
        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})

        response = self._client_admin.delete(single_event_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_creator_cant_destroy_event(self):
        event = baker.make(Event, user=self._user_admin, status=Event.Status.RUNNING)
        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})

        response = self._client_general.delete(single_event_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_create_event_in_occupied_venue(self):
        event = baker.make(
            Event,
            user=self._user_admin,
            status=Event.Status.RUNNING,
            tags=baker.make(EventTag, _quantity=3),
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        )
        data = {
            "name": "New Year Celebration",
            "venue": event.venue.id,
            "tags": [],
            "start_date": datetime.datetime(2022, 6, 2, 7, 30, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        }
        response = self._client_admin.post(self.EVENT_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_create_event_with_end_date_less_than_start_date(self):
        data = {
            "name": "New Year Celebration",
            "venue": baker.make(Venue).id,
            "tags": [tag.id for tag in baker.make(EventTag, _quantity=3)],
            "start_date": datetime.datetime(2021, 5, 10, 10, 20, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2021, 4, 10, 20, 30, tzinfo=pytz.UTC),
        }
        response = self._client_admin.post(self.EVENT_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_partial_update_fails_with_end_date_less_than_start_date(self):
        event = baker.make(
            Event,
            user=self._user_admin,
            status=Event.Status.RUNNING,
            tags=baker.make(EventTag, _quantity=3),
            venue=baker.make(Venue),
            start_date=datetime.datetime(2022, 6, 1, 7, 30, 30, tzinfo=pytz.UTC),
            end_date=datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        )

        single_event_url = reverse("events:event-detail", kwargs={"pk": event.id})
        data = {
            "start_date": datetime.datetime(2022, 7, 1, 7, 30, 30, tzinfo=pytz.UTC),
            "end_date": datetime.datetime(2022, 6, 5, 7, 30, 30, tzinfo=pytz.UTC),
        }
        response = self._client_admin.patch(single_event_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
