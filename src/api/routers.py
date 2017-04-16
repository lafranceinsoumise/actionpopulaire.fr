from rest_framework import routers

from people import viewsets as people_viewsets
from events import viewsets as events_viewsets

legacy_api = routers.DefaultRouter()

legacy_api.register('people', people_viewsets.LegacyPersonViewSet)
legacy_api.register('events', events_viewsets.LegacyEventViewSet)
legacy_api.register('calendars', events_viewsets.CalendarViewSet)


v1_api = routers.DefaultRouter()
v1_api.register('calendars', events_viewsets.CalendarViewSet)
