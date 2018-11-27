from django.urls import path

from . import views


urlpatterns = [
    path(
        "consultations/<uuid:pk>/",
        views.PollParticipationView.as_view(),
        name="participate_poll",
    ),
    path(
        "consultations/termine/", views.PollFinishedView.as_view(), name="finished_poll"
    ),
]
