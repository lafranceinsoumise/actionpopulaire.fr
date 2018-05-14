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
