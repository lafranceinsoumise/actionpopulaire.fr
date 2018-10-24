from django.urls import path

from . import views


urlpatterns = [
    path('evenements/creer/', views.CreateEventView.as_view(), name='create_event'),
    path('evenements/creer/form/', views.PerformCreateEventView.as_view(), name='perform_create_event'),
    path('evenements/liste/', views.EventListView.as_view(), name='list_all_events'),
    path('evenements/<uuid:pk>/', views.EventDetailView.as_view(), name='view_event'),
    path('evenements/<uuid:pk>/icalendar/', views.EventIcsView.as_view(), name='ics_event'),
    path('evenements/<uuid:pk>/manage/', views.ManageEventView.as_view(), name='manage_event'),
    path('evenements/<uuid:pk>/modifier/', views.ModifyEventView.as_view(), name='edit_event'),
    path('evenements/<uuid:pk>/quitter/', views.QuitEventView.as_view(), name='quit_event'),
    path('evenements/<uuid:pk>/annuler/', views.CancelEventView.as_view(), name='cancel_event'),
    path('evenements/<uuid:pk>/inscription/', views.RSVPEventView.as_view(), name='rsvp_event'),
    path('evenements/<uuid:pk>/inscription-externe/', views.ExternalRSVPView.as_view(), name='external_rsvp_event'),
    path('evenements/rsvp/<pk>/changer-paiement/', views.ChangeRSVPPaymentView.as_view(), name='rsvp_change_payment'),
    path('evenements/paiement/', views.PayEventView.as_view(), name='pay_event'),
    path('evenements/<uuid:pk>/localisation/', views.ChangeEventLocationView.as_view(), name='change_event_location'),
    path('evenements/<uuid:pk>/compte-rendu/', views.EditEventReportView.as_view(), name='edit_event_report'),
    path('evenements/<uuid:pk>/importer-image/', views.UploadEventImageView.as_view(),
        name='upload_event_image'),
    path('agenda/<slug:slug>/', views.CalendarView.as_view(), name='view_calendar'),
    path('agenda/<slug:slug>/icalendar/', views.CalendarIcsView.as_view(), name='ics_calendar')
]
