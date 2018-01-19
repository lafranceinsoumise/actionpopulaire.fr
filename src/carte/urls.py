from django.conf.urls import url
from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'

urlpatterns = [
    url('^liste_evenements/$', views.EventsView.as_view(), name='event_list'),
    url('^liste_groupes/$', views.GroupsView.as_view(), name='group_list'),
]
