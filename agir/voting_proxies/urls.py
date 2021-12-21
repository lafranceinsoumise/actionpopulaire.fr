from django.urls import path

from agir.voting_proxies.views import (
    VotingProxyRequestCreateAPIView,
    CommuneOrConsulateSearchAPIView,
    VotingProxyCreateAPIView,
)

urlpatterns = [
    path(
        "api/procurations/communes-consulats/",
        CommuneOrConsulateSearchAPIView.as_view(),
        name="api_commune_or_consulate_search",
    ),
    path(
        "api/procurations/demande/",
        VotingProxyRequestCreateAPIView.as_view(),
        name="api_create_voting_proxy_request",
    ),
    path(
        "api/procurations/volontaire/",
        VotingProxyCreateAPIView.as_view(),
        name="api_create_voting_proxy",
    ),
]
