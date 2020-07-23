from django.urls import path, include

urlpatterns = [
    path("", include("agir.front.urls")),
    path("", include("agir.people.urls")),
    path("", include("agir.elus.urls")),
    path("", include("agir.groups.urls")),
    path("", include("agir.events.urls")),
    path("", include("agir.payments.urls")),
    path("", include("agir.donations.urls")),
    path("", include("agir.polls.urls")),
    path("", include("agir.authentication.urls")),
    path("", include("agir.notifications.urls")),
    path("", include("agir.loans.urls")),
    path("", include("agir.municipales.urls")),
    path("", include("social_django.urls", namespace="social")),
    path("data-france/", include("data_france.urls")),
]
