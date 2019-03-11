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
]
