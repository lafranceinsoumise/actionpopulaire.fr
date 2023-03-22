from django.urls import path

from . import views

app_name = "ilb"

urlpatterns = [
    path(
        "dons/",
        views.PersonalInformationView.as_view(),
        name="personal_information",
    ),
]
