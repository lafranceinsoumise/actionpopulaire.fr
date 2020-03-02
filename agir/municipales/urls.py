from django.urls import path

from agir.municipales.views import (
    CommuneView,
    SearchView,
    CommuneChangeView,
    CommuneLoanView,
    CommuneLoanPersonalInformationView,
    CommuneLoanAcceptContractView,
    CommuneProcurationView,
    CommuneCostCertificateFormView,
    CommuneCostCertificateDownloadView,
)

urlpatterns = (
    path("communes/chercher/", SearchView.as_view(), name="search_commune"),
    path(
        "communes/<str:code_departement>/<str:slug>/",
        CommuneView.as_view(),
        name="view_commune",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/modifier/",
        CommuneChangeView.as_view(),
        name="change_commune",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/procuration/",
        CommuneProcurationView.as_view(),
        name="procuration_commune",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/prets/",
        CommuneLoanView.as_view(),
        name="municipales_loans_ask_amount",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/prets/informations/",
        CommuneLoanPersonalInformationView.as_view(),
        name="municipales_loans_personal_information",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/prets/contrat/",
        CommuneLoanAcceptContractView.as_view(),
        name="municipales_loans_contract",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/certificat/",
        CommuneCostCertificateFormView.as_view(),
        name="municipales_certificate_form",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/certificat/download",
        CommuneCostCertificateDownloadView.as_view(),
        name="municipales_certificate_download",
    ),
)
