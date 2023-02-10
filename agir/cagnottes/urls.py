from django.urls import path

from . import views

app_name = "cagnottes"

urlpatterns = [
    path(
        "<slug:slug>/informations/",
        views.PersonalInformationView.as_view(),
        name="personal_information",
    ),
    path("<slug:slug>/compteur/", views.CompteurView.as_view(), name="compteur"),
    path("<slug:slug>/montant/", views.ProgressView.as_view(), name="progress"),
]
