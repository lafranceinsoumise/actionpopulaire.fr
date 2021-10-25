from django.urls import path

from agir.presidentielle2022.views import (
    Donation2022PersonalInformationView,
    MonthlyDonation2022PersonalInformationView,
    MonthlyDonation2022EmailConfirmationView,
)

urlpatterns = [
    path(
        "2022/dons/informations/",
        Donation2022PersonalInformationView.as_view(),
        name="donation_2022_information",
    ),
    path(
        "2022/dons-mensuels/informations/",
        MonthlyDonation2022PersonalInformationView.as_view(),
        name="monthly_donation_2022_information",
    ),
    path(
        "2022/dons-mensuels/confirmer/",
        MonthlyDonation2022EmailConfirmationView.as_view(),
        name="monthly_donation_2022_confirm",
    ),
]
