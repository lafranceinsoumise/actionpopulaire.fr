from django.urls import path

from agir.elections.views import (
    VotingCommuneOrConsulateSearchAPIView,
    RetrieveCreatePollingStationOfficerAPIView,
    VotingCirconscriptionConsulaireAPIView,
)

urlpatterns = [
    path(
        "api/elections/communes-consulats/",
        VotingCommuneOrConsulateSearchAPIView.as_view(),
        name="api_voting_commune_or_consulate_search",
    ),
    path(
        "api/elections/circonscriptions-legislatives/",
        VotingCirconscriptionConsulaireAPIView.as_view(),
        name="api_list_circonscription_legislatives",
    ),
    path(
        "api/elections/assesseure-deleguee/",
        RetrieveCreatePollingStationOfficerAPIView.as_view(),
        name="api_retrieve_create_polling_station_officer",
    ),
]
