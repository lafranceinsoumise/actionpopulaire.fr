from django.conf.urls import url, include

from agir.front import urls as front_urls
from agir.events import urls as events_urls
from agir.groups import urls as groups_urls
from agir.donations import urls as donations_urls
from agir.payments import urls as payments_urls
from agir.people import urls as people_urls
from agir.polls import urls as polls_urls

urlpatterns = [
    url(r'^', include(front_urls)),
    url(r'^', include(people_urls)),
    url(r'^', include(groups_urls)),
    url(r'^', include(events_urls)),
    url(r'^', include(payments_urls)),
    url(r'^', include(donations_urls)),
    url(r'^', include(polls_urls)),
]
