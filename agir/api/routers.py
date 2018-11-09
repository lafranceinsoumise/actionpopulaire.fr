from rest_framework.routers import DefaultRouter

from ..people import viewsets as people_viewsets
from ..events import viewsets as events_viewsets
from ..groups import viewsets as groups_viewsets
from ..clients import viewsets as clients_viewsets

legacy_api = DefaultRouter()

# people routes
legacy_api.register('people', people_viewsets.LegacyPersonViewSet)
legacy_api.register('people_tags', people_viewsets.PersonTagViewSet)

# events route
events_route = legacy_api.register('events', events_viewsets.LegacyEventViewSet, base_name='event')
legacy_api.register('events_subtypes', events_viewsets.EventSubtypeViewSet)
legacy_api.register('calendars', events_viewsets.CalendarViewSet)
legacy_api.register('event_tags', events_viewsets.EventTagViewSet)
legacy_api.register('rsvps', events_viewsets.RSVPViewSet)

# groups routes
groups_route = legacy_api.register('groups', groups_viewsets.LegacySupportGroupViewSet)
legacy_api.register('groups_subtypes', groups_viewsets.SupportGroupSubtypeViewSet)
legacy_api.register('group_tags', groups_viewsets.SupportGroupTagViewSet)
legacy_api.register('memberships', groups_viewsets.MembershipViewSet)

# client and auth routes
legacy_api.register('scopes', clients_viewsets.ScopeViewSet, base_name='scopes')

urlpatterns = legacy_api.urls
