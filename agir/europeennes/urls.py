from django.urls import path

from . import views


urlpatterns = [
    path(
        "europeennes/dons/",
        views.DonationAskAmountView.as_view(),
        name="europeennes_donation_amount",
    ),
    path(
        "europeennes/dons/informations/",
        views.DonationPersonalInformationView.as_view(),
        name="europeennes_donation_information",
    ),
    path(
        "europeennes/prets/",
        views.LoanAskAmountView.as_view(),
        name="europeennes_loan_amount",
    ),
    path(
        "europeennes/prets/informations/",
        views.LoanPersonalInformationView.as_view(),
        name="europeennes_loan_information",
    ),
    path(
        "europeennes/prets/contrat/",
        views.LoanContractView.as_view(),
        name="europeennes_loan_sign_contract",
    ),
]
