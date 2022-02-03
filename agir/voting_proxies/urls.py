from django.urls import path

from agir.voting_proxies.views import (
    VotingProxyRequestCreateAPIView,
    CommuneOrConsulateSearchAPIView,
    VotingProxyCreateAPIView,
    VotingProxyRetrieveUpdateAPIView,
    ReplyToVotingProxyRequestsAPIView,
    VotingProxyForRequestRetrieveAPIView,
    VotingProxyRequestConfirmAPIView,
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
        "api/procurations/demande/<uuid:pk>/volontaire/",
        VotingProxyForRequestRetrieveAPIView.as_view(),
        name="api_retrieve_voting_proxy_for_request",
    ),
    path(
        "api/procurations/demande/confirmer/",
        VotingProxyRequestConfirmAPIView.as_view(),
        name="api_confirm_voting_proxy_request",
    ),
    path(
        "api/procurations/volontaire/",
        VotingProxyCreateAPIView.as_view(),
        name="api_create_voting_proxy",
    ),
    path(
        "api/procurations/volontaire/<uuid:pk>/",
        VotingProxyRetrieveUpdateAPIView.as_view(),
        name="api_retrieve_update_voting_proxy",
    ),
    path(
        "api/procurations/volontaire/<uuid:pk>/demandes/",
        ReplyToVotingProxyRequestsAPIView.as_view(),
        name="api_reply_to_voting_proxy_requests",
    ),
]