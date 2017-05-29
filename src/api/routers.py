from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework import routers

from people import viewsets as people_viewsets
from events import viewsets as events_viewsets
from groups import viewsets as groups_viewsets
from clients import viewsets as clients_viewsets

legacy_api = ExtendedSimpleRouter()

legacy_api.register('people', people_viewsets.LegacyPersonViewSet)
legacy_api.register('people_tags', people_viewsets.PersonTagViewSet)
events_route = legacy_api.register('events', events_viewsets.LegacyEventViewSet)
legacy_api.register('calendars', events_viewsets.CalendarViewSet)
legacy_api.register('event_tags', events_viewsets.EventTagViewSet)
legacy_api.register('rsvps', events_viewsets.RSVPViewSet)
events_route.register('rsvps', events_viewsets.NestedRSVPViewSet, base_name='events-rsvps', parents_query_lookups=['event'])
groups_route = legacy_api.register('groups', groups_viewsets.LegacySupportGroupViewSet)
legacy_api.register('group_tags', groups_viewsets.SupportGroupTagViewSet)
legacy_api.register('memberships', groups_viewsets.MembershipViewSet)
groups_route.register('memberships', groups_viewsets.NestedMembershipViewSet, base_name='supportgroup-memberships', parents_query_lookups=['supportgroup'])
legacy_api.register('clients', clients_viewsets.LegacyClientViewSet)

v1_api = routers.DefaultRouter()
v1_api.register('people_tags', people_viewsets.PersonTagViewSet)
v1_api.register('calendars', events_viewsets.CalendarViewSet)
v1_api.register('event_tags', events_viewsets.EventTagViewSet)
v1_api.register('group_tags', groups_viewsets.SupportGroupTagViewSet)
