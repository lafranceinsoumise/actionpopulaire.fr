from django.urls import path

from . import views

app_name = "elus"
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
    path(
        "mandat/departemental/",
        views.CreerMandatDepartementalView.as_view(),
        name="creer_mandat_departemental",
    ),
    path(
        "mandat/departemental/<int:pk>/",
        views.ModifierMandatDepartementalView.as_view(),
        name="modifier_mandat_departemental",
    ),
    path(
        "mandat/departemental/<int:pk>/supprimer/",
        views.SupprimerMandatDepartementalView.as_view(),
        name="supprimer_mandat_departemental",
    ),
    path(
        "mandat/regional/",
        views.CreerMandatRegionalView.as_view(),
        name="creer_mandat_regional",
    ),
    path(
        "mandat/regional/<int:pk>/",
        views.ModifierMandatRegionalView.as_view(),
        name="modifier_mandat_regional",
    ),
    path(
        "mandat/regional/<int:pk>/supprimer/",
        views.SupprimerMandatRegionalView.as_view(),
        name="supprimer_mandat_regional",
    ),
]
