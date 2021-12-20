from rest_framework.routers import SimpleRouter

from apps.events.views import EventViewSet, EventTagViewSet, EventSeatTypeViewSet, EventSeatViewSet

event_router = SimpleRouter(trailing_slash=False)
event_router.register(r"events", EventViewSet)
event_router.register(r"event_tags", EventTagViewSet)
event_router.register(r"event_seat_types", EventSeatTypeViewSet)
event_router.register(r"event_seats", EventSeatViewSet)

app_name = "events"
urlpatterns = event_router.urls
