from django.urls import path

from . import views
from agir.front.views import BaseAppView

urlpatterns = [
    path(
        "evenements/<uuid:pk>/og-image/",
        views.EventThumbnailView.as_view(),
        name="view_og_image_event",
    ),
    path("evenements/liste/", views.EventSearchView.as_view(), name="search_event"),
    path(
        "evenements/<uuid:pk>/participer/",
        views.EventParticipationView.as_view(),
        name="view_event_participation",
    ),
    path(
        "evenements/<uuid:pk>/icalendar/",
        views.EventIcsView.as_view(),
        name="ics_event",
    ),
    # path(
    #     "evenements/<uuid:pk>/manage/",
    #     views.ManageEventView.as_view(),
    #     name="manage_event",
    # ),
    path("evenements/<uuid:pk>/gestion/", BaseAppView, name="manage_event",),
    path(
        "evenements/<uuid:pk>/modifier/",
        views.ModifyEventView.as_view(),
        name="edit_event",
    ),
    path(
        "evenements/<uuid:pk>/quitter/",
        views.QuitEventView.as_view(),
        name="quit_event",
    ),
    path(
        "evenements/<uuid:pk>/annuler/",
        views.CancelEventView.as_view(),
        name="cancel_event",
    ),
    path(
        "evenements/<uuid:pk>/inscription/",
        views.RSVPEventView.as_view(),
        name="rsvp_event",
    ),
    path(
        "evenements/<uuid:pk>/inscription-externe/",
        views.ExternalRSVPView.as_view(),
        name="external_rsvp_event",
    ),
    path(
        "evenements/rsvp/<pk>/changer-paiement/",
        views.ChangeRSVPPaymentView.as_view(),
        name="rsvp_change_payment",
    ),
    path("evenements/paiement/", views.PayEventView.as_view(), name="pay_event"),
    path(
        "evenements/<uuid:pk>/localisation/",
        views.ChangeEventLocationView.as_view(),
        name="change_event_location",
    ),
    path(
        "evenements/<uuid:pk>/compte-rendu/",
        views.EditEventReportView.as_view(),
        name="edit_event_report",
    ),
    path(
        "evenements/<uuid:pk>/legal/",
        views.EditEventLegalView.as_view(),
        name="event_legal_form",
    ),
    path(
        "evenements/<uuid:pk>/importer-image/",
        views.UploadEventImageView.as_view(),
        name="upload_event_image",
    ),
    path(
        "evenements/<uuid:pk>/envoyer-compte-rendu/",
        views.SendEventReportView.as_view(),
        name="send_event_report",
    ),
    path("agenda/<slug:slug>/", views.CalendarView.as_view(), name="view_calendar"),
    path(
        "agenda/<slug:slug>/icalendar/",
        views.CalendarIcsView.as_view(),
        name="ics_calendar",
    ),
    path("conference", views.jitsi_reservation_view, name="jitsi_reservation"),
    path(
        "conference/<int:pk>", views.jitsi_delete_conference_view, name="jitsi_delete"
    ),
    path(
        "api/evenements/options/",
        views.EventCreateOptionsAPIView.as_view(),
        name="api_event_create_options",
    ),
    path(
        "api/evenements/creer/",
        views.CreateEventAPIView.as_view(),
        name="api_create_event",
    ),
    path(
        "api/evenements/<uuid:pk>/modifier/",
        views.UpdateEventAPIView.as_view(),
        name="api_update_event",
    ),
    path(
        "api/evenements/rsvped/",
        views.EventRsvpedAPIView.as_view(),
        name="api_event_rsvped",
    ),
    path(
        "api/evenements/suggestions/",
        views.EventSuggestionsAPIView.as_view(),
        name="api_event_suggestions",
    ),
    path(
        "api/evenements/projets/",
        views.EventProjectsAPIView.as_view(),
        name="api_event_projects",
    ),
    path(
        "api/evenements/<uuid:pk>/",
        views.EventDetailAPIView.as_view(),
        name="api_event_view",
    ),
    path(
        "api/evenements/<uuid:pk>/inscription/",
        views.RSVPEventAPIView.as_view(),
        name="api_rsvp_event",
    ),
    path(
        "api/evenements/<uuid:event_id>/projet/",
        views.EventProjectAPIView.as_view(),
        name="api_event_project",
    ),
    path(
        "api/evenements/<uuid:event_id>/projet/document/",
        views.CreateEventProjectDocumentAPIView.as_view(),
        name="api_create_event_project_document",
    ),
]
