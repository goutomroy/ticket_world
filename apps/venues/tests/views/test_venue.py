from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.venues.models import Venue


class VenueAPITestCase(APITestCase):

    VENUE_LIST_PATH = reverse("venues:venue-list")

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

    def test_admin_can_create_venue(self):
        data = {
            "name": "Central Hall",
            "address": "Gulshan-2, Dhaka",
            "location": {"x": 10.5, "y": 10.5},
        }
        response = self._client_admin.post(self.VENUE_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_can_create_venue(self):
        data = {
            "name": "Central Hall",
            "address": "Gulshan-2, Dhaka",
            "location": {"x": 10.5, "y": 10.5},
        }
        response = self._client_staff.post(self.VENUE_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_general_user_cant_create_venue(self):
        data = {
            "name": "Central Hall",
            "address": "Gulshan-2, Dhaka",
            "location": {"x": 10.5, "y": 10.5},
        }
        response = self._client_general.post(self.VENUE_LIST_PATH, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_can_read_venue_list(self):
        self.assertEqual(
            self._client_admin.get(self.VENUE_LIST_PATH).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self._client_staff.get(self.VENUE_LIST_PATH).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self._client_general.get(self.VENUE_LIST_PATH).status_code,
            status.HTTP_200_OK,
        )

    def test_anyone_can_retrieve_single_venue(self):
        venue_detail_url = reverse(
            "venues:venue-detail", kwargs={"pk": baker.make(Venue).id}
        )
        self.assertEqual(
            self._client_admin.get(venue_detail_url).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self._client_staff.get(venue_detail_url).status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            self._client_general.get(venue_detail_url).status_code, status.HTTP_200_OK
        )

    def test_admin_can_update_destroy_single_venue(self):
        venue_detail_url = reverse(
            "venues:venue-detail", kwargs={"pk": baker.make(Venue).id}
        )

        response = self._client_admin.put(
            venue_detail_url,
            {
                "name": "any update",
                "address": "Warsaw",
                "location": {"x": 10.5, "y": 10.5},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_admin.patch(
            venue_detail_url, {"name": "any update"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_admin.delete(venue_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_staff_can_update_destroy_single_venue(self):
        venue_detail_url = reverse(
            "venues:venue-detail", kwargs={"pk": baker.make(Venue).id}
        )

        response = self._client_staff.put(
            venue_detail_url,
            {
                "name": "any update",
                "address": "Warsaw",
                "location": {"x": 10.5, "y": 10.5},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_staff.patch(
            venue_detail_url, {"name": "any update"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self._client_staff.delete(venue_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_general_user_cant_update_destroy_single_venue(self):
        venue_detail_url = reverse(
            "venues:venue-detail", kwargs={"pk": baker.make(Venue).id}
        )

        response = self._client_general.put(
            venue_detail_url,
            {
                "name": "any update",
                "address": "Warsaw",
                "location": {"x": 10.5, "y": 10.5},
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self._client_general.patch(
            venue_detail_url, {"name": "any update"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self._client_general.delete(venue_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
