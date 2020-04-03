from django.urls import path, include

from data_france.views import CommuneSearchView

from agir.front import urls as front_urls
from agir.events import urls as events_urls
from agir.groups import urls as groups_urls
from agir.donations import urls as donations_urls
from agir.payments import urls as payments_urls
from agir.people import urls as people_urls
from agir.polls import urls as polls_urls
from agir.authentication import urls as authentication_urls
from agir.notifications import urls as notifications_urls
from agir.loans import urls as loans_urls
from agir.municipales import urls as municipales_urls


urlpatterns = [
    path("", include(front_urls)),
    path("", include(people_urls)),
    path("", include(groups_urls)),
    path("", include(events_urls)),
    path("", include(payments_urls)),
    path("", include(donations_urls)),
    path("", include(polls_urls)),
    path("", include(authentication_urls)),
    path("", include(notifications_urls)),
    path("", include(loans_urls)),
    path("", include(municipales_urls)),
    path("", include("social_django.urls", namespace="social")),
    path("chercher-commune/", CommuneSearchView.as_view()),
]
