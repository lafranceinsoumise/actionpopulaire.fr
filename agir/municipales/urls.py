from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from agir.municipales.views import (
    CommuneView,
    SearchView,
    CommuneChangeView,
    CommuneLoanView,
    CommuneLoanPersonalInformationView,
    CommuneLoanAcceptContractView,
    # CommuneProcurationView,
    CommuneCostCertificateFormView,
    CommuneCostCertificateDownloadView,
)

urlpatterns = (
    path("communes/chercher/", SearchView.as_view(), name="search_commune"),
    path(
        "communes/<str:code_departement>/<str:slug>/",
        CommuneView.as_view(tour=2),
        name="view_commune",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/modifier/",
        CommuneChangeView.as_view(),
        name="change_commune",
    ),
    path(
        "communes/<str:code_departement>/<str:slug>/procuration/",
        # CommuneProcurationView.as_view(),
        RedirectView.as_view(
            url=reverse_lazy("voting_proxy_landing_page"), permanent=False
        ),
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
