from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path
from django.views.generic import RedirectView

from .views import ActivityView, RequiredActivityView
from .views import AgendaView
from .views import NSPView
from ..front.sitemaps import sitemaps
from . import views

urlpatterns = [
    path("nsp/", NSPView.as_view(), name="nsp"),
    # https://lafranceinsoumise.fr/
    path("homepage/", RedirectView.as_view(url=settings.MAIN_DOMAIN), name="homepage"),
    # sitemap
    path("sitemap.xml", sitemap_index, {"sitemaps": sitemaps}),
    path(
        "sitemap-<section>.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # old redirections
    path(
        "groupes/",
        RedirectView.as_view(url=reverse_lazy("dashboard")),
        name="list_groups",
    ),
    path("activite/", ActivityView.as_view(), name="list_activities",),
    path(
        "a-traiter/", RequiredActivityView.as_view(), name="list_required_activities",
    ),
    path("evenements/", AgendaView.as_view(), name="list_events",),
    path("mes-groupes/", views.MyGroupsView.as_view(), name="list_my_groups"),
    path("navigation/", views.NavigationMenuView.as_view(), name="navigation_menu"),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
