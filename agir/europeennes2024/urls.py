from django.urls import path

from . import views

app_name = "europeennes2024"

urlpatterns = [
    path(
        "prets/informations/",
        views.PretsPersonalInformationView.as_view(),
        name="information_prets",
    ),
    path(
        "prets/contrat/", views.PretsReviewContractView.as_view(), name="contrat_prets"
    ),
    path(
        "dons/informations/",
        views.DonsPersonalInformationView.as_view(),
        name="informations_dons",
    ),
    path("montant/", views.MontantView.as_view(), name="montant"),
    path("compteur/", views.CompteurView.as_view(), name="compteur"),
]
