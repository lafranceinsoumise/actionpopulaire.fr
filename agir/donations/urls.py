from django.urls import path

from . import views


urlpatterns = [
    path("dons/", views.AskAmountView.as_view(), name="donation_amount"),
    path(
        "dons/informations/",
        views.PersonalInformationView.as_view(),
        name="donation_information",
    ),
]
