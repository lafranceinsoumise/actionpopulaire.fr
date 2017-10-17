from django.conf.urls import url

from . import views, oauth

urlpatterns = [
    # people views
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

    # events views
    url('^evenements/$', views.EventListView.as_view(), name='list_events'),
    url('^evenements/creer/$', views.CreateEventView.as_view(), name='create_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/$', views.EventDetailView.as_view(), name='view_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/manage/$', views.ManageEventView.as_view(), name='manage_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/modifier/$', views.ModifyEventView.as_view(), name='edit_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/quitter/$', views.QuitEventView.as_view(), name='quit_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/annuler/$', views.CancelEventView.as_view(), name='cancel_event'),
    url('^agenda/(?P<slug>[-a-zA-Z0-9_]+)/$', views.CalendarView.as_view(), name='view_calendar'),

    # groups views
    url('^groupes/$', views.SupportGroupListView.as_view(), name='list_groups'),
    url('^groupes/creer/$', views.CreateSupportGroupView.as_view(), name='create_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/$', views.SupportGroupDetailView.as_view(), name='view_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/manage/$', views.SupportGroupManagementView.as_view(), name='manage_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/modifier/$', views.ModifySupportGroupView.as_view(), name='edit_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/quitter/$', views.QuitSupportGroupView.as_view(), name='quit_group'),

    url('^groupes/retirer_gestionnaire/(?P<pk>[0-9a-f-]+)/$', views.RemoveManagerView.as_view(), name='remove_manager'),

    url('^livrets_thematiques/$', views.ThematicBookletViews.as_view(), name="thematic_groups_list"),

    # old urls
    url('^old(.*)', views.NBUrlsView.as_view(), name='old_urls'),

    # authentication views
    url('^authentification/$', oauth.OauthRedirectView.as_view(), name='oauth_redirect_view'),
    url('^authentification/retour/$', oauth.OauthReturnView.as_view(), name='oauth_return_view'),
    url('^deconnexion/$', oauth.LogOffView.as_view(), name='oauth_disconnect')
]
