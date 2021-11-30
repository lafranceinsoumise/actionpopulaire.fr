from django.urls import path

from agir.presidentielle2022.views import (
    MonthlyDonation2022EmailConfirmationView,
    PublicDonation2022AggregatesAPIView,
    Donation2022AggregatesAPIView,
)

urlpatterns = [
    path(
        "2022/dons-mensuels/confirmer/",
        MonthlyDonation2022EmailConfirmationView.as_view(),
        name="monthly_donation_2022_confirm",
    ),
    path(
        "api/2022/dons/",
        PublicDonation2022AggregatesAPIView.as_view(),
        name="api_public_donation_aggregates_2022",
    ),
    path(
        "api/2022/dons/aggregats/",
        Donation2022AggregatesAPIView.as_view(),
        name="api_donation_2022_aggregates",
    ),
]
