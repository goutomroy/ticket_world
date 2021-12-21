from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.venues.models import Venue
from apps.venues.serializers import VenueSerializer


class VenueViewSet(ModelViewSet):

    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (DjangoFilterBackend,)
