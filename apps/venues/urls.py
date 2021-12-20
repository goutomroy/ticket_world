from rest_framework.routers import SimpleRouter

from apps.venues.views import VenueViewSet

venues_router = SimpleRouter(trailing_slash=False)
venues_router.register(r"venues", VenueViewSet)

app_name = "venues"
urlpatterns = venues_router.urls
