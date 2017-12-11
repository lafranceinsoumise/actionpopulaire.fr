from django.conf.urls import url

from . import views, oauth

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    # people views
    url('^desinscription/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/succes/$', views.UnsubscribeSuccessView.as_view(), name='unsubscribe_success'),
    url('^inscription/$', views.SimpleSubscriptionView.as_view(), name='subscription'),
    url('^inscription/etranger/$', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    url('^inscription/succes/$', views.SubscriptionSuccessView.as_view(), name='subscription_success'),
    url('^profil/$', views.ChangeProfileView.as_view(), name='change_profile'),
    url('^profil/confirmation/$', views.ChangeProfileConfirmationView.as_view(), name='confirmation_profile'),
    url('^agir/$', views.VolunteerView.as_view(), name='volunteer'),
    url('^agir/confirmation/$', views.VolunteerConfirmationView.as_view(), name='confirmation_volunteer'),
    url('^message_preferences/$', views.MessagePreferencesView.as_view(), name='message_preferences'),
    url('^message_preferences/adresses/$', views.EmailManagementView.as_view(), name='email_management'),
    url(f'^message_preferences/adresses/(?P<pk>{simple_id})/supprimer/$', views.DeleteEmailAddressView.as_view(), name='delete_email'),
    url('^formulaires/(?P<slug>[-a-zA-Z0-9_]+)/$', views.PeopleFormView.as_view(), name='view_person_form'),
    url('^formulaires/(?P<slug>[-a-zA-Z0-9_]+)/confirmation/$', views.PeopleFormConfirmationView.as_view(), name='person_form_confirmation'),

    # dashboard
    url('^$', views.DashboardView.as_view(), name='dashboard'),

    # events views
    url('^evenements/$', views.EventListView.as_view(), name='list_events'),
    url('^evenements/creer/$', views.CreateEventView.as_view(), name='create_event'),
    url(f'^evenements/(?P<pk>{uuid})/$', views.EventDetailView.as_view(), name='view_event'),
    url(f'^evenements/(?P<pk>{uuid})/manage/$', views.ManageEventView.as_view(), name='manage_event'),
    url(f'^evenements/(?P<pk>{uuid})/modifier/$', views.ModifyEventView.as_view(), name='edit_event'),
    url(f'^evenements/(?P<pk>{uuid})/quitter/$', views.QuitEventView.as_view(), name='quit_event'),
    url(f'^evenements/(?P<pk>{uuid})/annuler/$', views.CancelEventView.as_view(), name='cancel_event'),
    url(f'^evenements/(?P<pk>{uuid})/localisation/$', views.ChangeEventLocationView.as_view(), name='change_event_location'),
    url(f'^evenements/(?P<pk>{uuid})/compte-rendu/$', views.EditEventReportView.as_view(), name='edit_event_report'),
    url(f'^evenements/(?P<pk>{uuid})/importer-image/$', views.UploadEventImageView.as_view(), name='upload_event_image'),
    url('^agenda/(?P<slug>[-a-zA-Z0-9_]+)/$', views.CalendarView.as_view(), name='view_calendar'),

    # groups views
    url('^groupes/$', views.SupportGroupListView.as_view(), name='list_groups'),
    url('^groupes/creer/$', views.CreateSupportGroupView.as_view(), name='create_group'),
    url(f'^groupes/(?P<pk>{uuid})/$', views.SupportGroupDetailView.as_view(), name='view_group'),
    url(f'^groupes/(?P<pk>{uuid})/manage/$', views.SupportGroupManagementView.as_view(), name='manage_group'),
    url(f'^groupes/(?P<pk>{uuid})/modifier/$', views.ModifySupportGroupView.as_view(), name='edit_group'),
    url(f'^groupes/(?P<pk>{uuid})/quitter/$', views.QuitSupportGroupView.as_view(), name='quit_group'),
    url(f'^groupes/(?P<pk>{uuid})/localisation/$', views.ChangeGroupLocationView.as_view(), name='change_group_location'),

    url(f'^groupes/retirer_gestionnaire/(?P<pk>{simple_id})/$', views.RemoveManagerView.as_view(), name='remove_manager'),

    url('^livrets_thematiques/$', views.ThematicBookletViews.as_view(), name="thematic_groups_list"),

    # polls views
    url(f'^consultations/(?P<pk>{uuid})/$', views.PollParticipationView.as_view(), name='participate_poll'),
    url(f'^consultations/termine/$', views.PollFinishedView.as_view(), name='finished_poll'),

    # old urls
    url('^old(.*)', views.NBUrlsView.as_view(), name='old_urls'),

    # authentication views
    url('^authentification/$', oauth.OauthRedirectView.as_view(), name='oauth_redirect_view'),
    url('^authentification/retour/$', oauth.OauthReturnView.as_view(), name='oauth_return_view'),
    url('^deconnexion/$', oauth.LogOffView.as_view(), name='oauth_disconnect')
]
