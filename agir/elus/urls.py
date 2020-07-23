from django.urls import path, reverse_lazy
from django.views.generic import TemplateView, RedirectView

from . import views

urlpatterns = [
    path(
        "mandat/municipal/",
        views.CreerMandatMunicipalView.as_view(),
        name="creer_mandat_municipal",
    ),
    path(
        "mandat/municipal/<int:pk>/",
        views.ModifierMandatMunicipalView.as_view(),
        name="modifier_mandat_municipal",
    ),
    path(
        "mandat/municipal/<int:pk>/supprimer/",
        views.SupprimerMandatMunicipalView.as_view(),
        name="supprimer_mandat_municipal",
    ),
]
