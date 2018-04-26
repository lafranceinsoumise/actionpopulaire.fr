from django.conf.urls import url, include

import front.urls
import donations.urls
import payments.urls

urlpatterns = [
    url(r'^', include(front.urls)),
    url(r'^', include(donations.urls)),
    url(r'^', include(payments.urls))
]
