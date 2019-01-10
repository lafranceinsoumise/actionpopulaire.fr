from django.urls import path

from . import views


urlpatterns = [
    path(
        "europeennes/dons/",
        views.AskAmountView.as_view(),
        name="europeennes_donation_amount",
    ),
    path(
        "europeennes/dons/informations/",
        views.PersonalInformationView.as_view(),
        name="europeennes_donation_information",
    ),
]
