from django.conf.urls import url

from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    url(f'^consultations/(?P<pk>{uuid})/$', views.PollParticipationView.as_view(), name='participate_poll'),
    url(f'^consultations/termine/$', views.PollFinishedView.as_view(), name='finished_poll'),
]
