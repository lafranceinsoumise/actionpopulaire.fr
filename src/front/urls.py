from django.conf import settings
from django.conf.urls import url
from django.contrib.sitemaps.views import sitemap
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from front.sitemaps import sitemaps
from . import views, oauth

uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
simple_id = r'[0-9]+'


urlpatterns = [
    # https://lafranceinsoumise.fr/
    url('^homepage/$', RedirectView.as_view(url=settings.MAIN_DOMAIN), name='homepage'),
    # sitemap
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    # people views
    url('^desinscription/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/$', views.UnsubscribeView.as_view(), name='unsubscribe'),
    url('^desabonnement/succes/$', TemplateView.as_view(template_name='front/people/unsubscribe_success.html'), name='unsubscribe_success'),
    url('^supprimer/$', views.DeleteAccountView.as_view(), name='delete_account'),
    url('^supprimer/succes$', TemplateView.as_view(template_name='front/people/delete_account_success.html'), name='delete_account_success'),
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
    url('^evenements/$', RedirectView.as_view(url=reverse_lazy('dashboard')), name='list_events'),

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
