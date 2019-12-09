from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path
from django.views.generic import RedirectView

from ..front.sitemaps import sitemaps
from . import views

urlpatterns = [
    # https://lafranceinsoumise.fr/
    path("homepage/", RedirectView.as_view(url=settings.MAIN_DOMAIN), name="homepage"),
    # sitemap
    path(
        "sitemap.xml",
        sitemap_index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
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
    path(
        "evenements/",
        RedirectView.as_view(url=reverse_lazy("dashboard")),
        name="list_events",
    ),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
