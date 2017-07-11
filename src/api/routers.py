from rest_framework_extensions.routers import ExtendedDefaultRouter

from people import viewsets as people_viewsets
from events import viewsets as events_viewsets
from groups import viewsets as groups_viewsets
from clients import viewsets as clients_viewsets

legacy_api = ExtendedDefaultRouter()

# people routes
legacy_api.register('people', people_viewsets.LegacyPersonViewSet)
legacy_api.register('people_tags', people_viewsets.PersonTagViewSet)

# events route
events_route = legacy_api.register('events', events_viewsets.LegacyEventViewSet, base_name='event')
legacy_api.register('calendars', events_viewsets.CalendarViewSet)
legacy_api.register('event_tags', events_viewsets.EventTagViewSet)
legacy_api.register('rsvps', events_viewsets.RSVPViewSet)
events_route.register('rsvps', events_viewsets.NestedRSVPViewSet, base_name='events-rsvps', parents_query_lookups=['event'])

# groups routes
groups_route = legacy_api.register('groups', groups_viewsets.LegacySupportGroupViewSet)
legacy_api.register('group_tags', groups_viewsets.SupportGroupTagViewSet)
legacy_api.register('memberships', groups_viewsets.MembershipViewSet)
groups_route.register('memberships', groups_viewsets.NestedMembershipViewSet, base_name='supportgroup-memberships', parents_query_lookups=['supportgroup'])

# client and auth routes
legacy_api.register('clients', clients_viewsets.LegacyClientViewSet)
legacy_api.register('scopes', clients_viewsets.ScopeViewSet)
legacy_api.register('authorizations', clients_viewsets.AuthorizationViewSet)
