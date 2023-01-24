from django.urls import include, path

from . import views

api_urlpatterns = [
    path(
        "intervenant-e/",
        views.EventSpeakerRetrieveUpdateAPIView.as_view(),
        name="api_event_speaker_retrieve_update",
    ),
    path(
        "intervenant-e/evenements-a-venir/",
        views.EventSpeakerEventListAPIView.as_view(),
        name="api_event_speaker_event_list",
    ),
    path(
        "disponibilite/<uuid:pk>/",
        views.EventSpeakerRequestRetrieveUpdateAPIView.as_view(),
        name="api_event_speaker_request_retrieve_update",
    ),
]

urlpatterns = [
    path("api/evenements/demandes/", include(api_urlpatterns)),
]
