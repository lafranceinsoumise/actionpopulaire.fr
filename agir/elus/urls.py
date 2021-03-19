from django.urls import path

from .views import gestion_mandats, recherche_parrainages

app_name = "elus"
urlpatterns = [
    path(
        "mandat/municipal/",
        gestion_mandats.CreerMandatMunicipalView.as_view(),
        name="creer_mandat_municipal",
    ),
    path(
        "mandat/municipal/<int:pk>/",
        gestion_mandats.ModifierMandatMunicipalView.as_view(),
        name="modifier_mandat_municipal",
    ),
    path(
        "mandat/municipal/<int:pk>/supprimer/",
        gestion_mandats.SupprimerMandatMunicipalView.as_view(),
        name="supprimer_mandat_municipal",
    ),
    path(
        "mandat/departemental/",
        gestion_mandats.CreerMandatDepartementalView.as_view(),
        name="creer_mandat_departemental",
    ),
    path(
        "mandat/departemental/<int:pk>/",
        gestion_mandats.ModifierMandatDepartementalView.as_view(),
        name="modifier_mandat_departemental",
    ),
    path(
        "mandat/departemental/<int:pk>/supprimer/",
        gestion_mandats.SupprimerMandatDepartementalView.as_view(),
        name="supprimer_mandat_departemental",
    ),
    path(
        "mandat/regional/",
        gestion_mandats.CreerMandatRegionalView.as_view(),
        name="creer_mandat_regional",
    ),
    path(
        "mandat/regional/<int:pk>/",
        gestion_mandats.ModifierMandatRegionalView.as_view(),
        name="modifier_mandat_regional",
    ),
    path(
        "mandat/regional/<int:pk>/supprimer/",
        gestion_mandats.SupprimerMandatRegionalView.as_view(),
        name="supprimer_mandat_regional",
    ),
    path(
        "parrainages/",
        recherche_parrainages.RechercheParrainagesView.as_view(),
        name="parrainages",
    ),
    path(
        "api/parrainages/chercher/",
        recherche_parrainages.ChercherEluView.as_view(),
        name="rechercher_parrainage",
    ),
    path(
        "api/parrainages/",
        recherche_parrainages.CreerRechercheParrainageView.as_view(),
        name="creer_parrainage",
    ),
    path(
        "api/parrainages/<int:pk>/",
        recherche_parrainages.ModifierRechercheParrainageView.as_view(),
        name="modifier_parrainage",
    ),
]
