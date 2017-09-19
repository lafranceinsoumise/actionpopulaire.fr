from django.conf.urls import url

from . import views, oauth

urlpatterns = [
    url('^inscription/$', views.SimpleSubscriptionView.as_view(), name='subscription'),
    url('^inscription/etranger/$', views.OverseasSubscriptionView.as_view(), name='subscription_overseas'),
    url('^inscription/succes/$', views.SubscriptionSuccessView.as_view(), name='subscription_success'),
    url('^profil/$', views.ChangeProfileView.as_view(), name='profile_change'),
    url('^agir/$', views.VolunteerPage.as_view(), name='volunteer'),
    url('^merci/$', views.ProfileConfirmationPage.as_view(), name="confirmation"),

    url('^evenements/$', views.EventListView.as_view(), name='list_events'),
    url('^evenements/creer/$', views.CreateEventView.as_view(), name='create_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/modifier/$', views.UpdateEventView.as_view(), name='edit_event'),
    url('^evenements/(?P<pk>[0-9a-f-]+)/quitter/$', views.QuitEventView.as_view(), name='quit_event'),

    url('^groupes/$', views.SupportGroupListView.as_view(), name='list_groups'),
    url('^groupes/creer/$', views.CreateSupportGroupView.as_view(), name='create_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/$', views.SupportGroupManagementView.as_view(), name='manage_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/modifier/$', views.UpdateSupportGroupView.as_view(), name='edit_group'),
    url('^groupes/(?P<pk>[0-9a-f-]+)/quitter/$', views.QuitSupportGroupView.as_view(), name='quit_group'),

    url('^groupes/retirer_gestionnaire/(?P<pk>[0-9a-f-]+)/$', views.RemoveManagerView.as_view(), name='remove_manager'),

    url('^authentification/$', oauth.OauthRedirectView.as_view(), name='oauth_redirect_view'),
    url('^authentification/retour/$', oauth.OauthReturnView.as_view(), name='oauth_return_view'),
    url('^deconnexion/$', oauth.LogOffView.as_view(), name='oauth_disconnect')
]
