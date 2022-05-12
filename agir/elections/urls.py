from django.urls import path

from agir.elections.views import (
    VotingCommuneOrConsulateSearchAPIView,
    RetrieveCreatePollingStationOfficerAPIView,
)

urlpatterns = [
    path(
        "api/elections/communes-consulats/",
        VotingCommuneOrConsulateSearchAPIView.as_view(),
        name="api_voting_commune_or_consulate_search",
    ),
    path(
        "api/elections/assesseure-deleguee/",
        RetrieveCreatePollingStationOfficerAPIView.as_view(),
        name="api_retrieve_create_polling_station_officer",
    ),
]
