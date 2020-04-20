from rest_framework.routers import DefaultRouter

from ..people import viewsets as people_viewsets
from ..clients import viewsets as clients_viewsets

legacy_api = DefaultRouter()

# people routes
legacy_api.register("people", people_viewsets.LegacyPersonViewSet)
legacy_api.register("people_tags", people_viewsets.PersonTagViewSet)

# client and auth routes
legacy_api.register("scopes", clients_viewsets.ScopeViewSet, basename="scopes")

app_name = "legacy"
urlpatterns = legacy_api.urls
