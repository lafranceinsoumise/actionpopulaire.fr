from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path
from django.views.generic import RedirectView

from . import views
from ..front.sitemaps import sitemaps

urlpatterns = [
    path("rejoindre/", views.JoinView.as_view(), name="join"),
    path("nsp/", views.NSPView.as_view(), name="nsp"),
    path("nsp/referral/", views.NSPReferralView.as_view(), name="nsp_referral"),
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
    path("groupes/carte/", views.GroupMapView.as_view(), name="group_map_page"),
    path(
        "groupes/<uuid:pk>/", views.SupportGroupDetailView.as_view(), name="view_group"
    ),
    path("activite/", views.ActivityView.as_view(), name="list_activities",),
    path(
        "a-traiter/",
        views.RequiredActivityView.as_view(),
        name="list_required_activities",
    ),
    path("", views.AgendaView.as_view(), name="dashboard",),
    path(
        "evenements/",
        RedirectView.as_view(pattern_name="dashboard"),
        name="list_events",
    ),
    path("evenements/carte/", views.EventMapView.as_view(), name="event_map_page"),
    path("evenements/<uuid:pk>/", views.EventDetailView.as_view(), name="view_event"),
    path("mes-groupes/", views.MyGroupsView.as_view(), name="list_my_groups"),
    path(
        "groupes/<uuid:pk>/complet/",
        views.FullSupportGroupView.as_view(),
        name="full_group",
    ),
    path("navigation/", views.NavigationMenuView.as_view(), name="navigation_menu"),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
