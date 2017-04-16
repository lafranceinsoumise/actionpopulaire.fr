from rest_framework import routers

from people import viewsets as people_viewsets

legacy_api = routers.SimpleRouter()

legacy_api.register('people', people_viewsets.LegacyPersonViewSet)
