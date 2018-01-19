from django.conf.urls import url
from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'

urlpatterns = [
    url('^liste_evenements/$', views.EventsView.as_view(), name='event_list'),
    url('^liste_groupes/$', views.GroupsView.as_view(), name='group_list'),
    url('^evenements/$', views.EventMapView.as_view(), name='events_map'),
    url(f'^evenements/(?P<pk>{uuid})/', views.SingleEventMapView.as_view(), name='single_event_map'),
    url('^groupes/$', views.GroupMapView.as_view(), name='groups_map'),
    url(f'^groupes/(?P<pk>{uuid})/', views.SingleGroupMapView.as_view(), name='single_group_map'),
]
