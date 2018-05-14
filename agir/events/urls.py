from django.conf.urls import url

from . import views

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    url('^evenements/creer/$', views.CreateEventView.as_view(), name='create_event'),
    url('^evenements/creer/form/$', views.PerformCreateEventView.as_view(), name='perform_create_event'),
    url('^evenements/liste/$', views.EventListView.as_view(), name='list_all_events'),
    url(f'^evenements/(?P<pk>{uuid})/$', views.EventDetailView.as_view(), name='view_event'),
    url(f'^evenements/(?P<pk>{uuid})/manage/$', views.ManageEventView.as_view(), name='manage_event'),
    url(f'^evenements/(?P<pk>{uuid})/modifier/$', views.ModifyEventView.as_view(), name='edit_event'),
    url(f'^evenements/(?P<pk>{uuid})/quitter/$', views.QuitEventView.as_view(), name='quit_event'),
    url(f'^evenements/(?P<pk>{uuid})/annuler/$', views.CancelEventView.as_view(), name='cancel_event'),
    url(f'^evenements/(?P<pk>{uuid})/inscription/$', views.RSVPEventView.as_view(), name='rsvp_event'),
    url(f'^evenements/paiement/$', views.PayEventView.as_view(), name='pay_event'),
    url(f'^evenements/(?P<pk>{uuid})/localisation/$', views.ChangeEventLocationView.as_view(), name='change_event_location'),
    url(f'^evenements/(?P<pk>{uuid})/compte-rendu/$', views.EditEventReportView.as_view(), name='edit_event_report'),
    url(f'^evenements/(?P<pk>{uuid})/importer-image/$', views.UploadEventImageView.as_view(),
        name='upload_event_image'),
    url('^agenda/(?P<slug>[-a-zA-Z0-9_]+)/$', views.CalendarView.as_view(), name='view_calendar'),
]
