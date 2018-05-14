from django.conf.urls import url, include

import front.urls
import events.urls
import groups.urls
import donations.urls
import payments.urls
import people.urls
import polls.urls

urlpatterns = [
    url(r'^', include(front.urls)),
    url(r'^', include(people.urls)),
    url(r'^', include(groups.urls)),
    url(r'^', include(events.urls)),
    url(r'^', include(payments.urls)),
    url(r'^', include(donations.urls)),
    url(r'^', include(polls.urls)),
]
