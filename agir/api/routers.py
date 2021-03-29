from rest_framework.routers import DefaultRouter

from ..clients import viewsets as clients_viewsets

legacy_api = DefaultRouter()

# client and auth routes
legacy_api.register("scopes", clients_viewsets.ScopeViewSet, basename="scopes")

app_name = "legacy"
urlpatterns = legacy_api.urls
