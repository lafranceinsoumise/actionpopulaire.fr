from django.urls import include, path

from . import views

api_urlpatterns = [
    path(
        "intervenant-e/",
        views.EventSpeakerRetrieveUpdateAPIView.as_view(),
        name="api_event_speaker_retrieve_update",
    ),
]

urlpatterns = [
    path("api/demandes-evenements/", include(api_urlpatterns)),
]
