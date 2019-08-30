from django.urls import path

from agir.municipales.views import CommuneView

urlpatterns = (
    path(
        "communes/<str:code_departement>/<str:slug>/",
        CommuneView.as_view(),
        name="view_commune",
    ),
)
