from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path
from django.views.generic import RedirectView

from . import views
from ..front.sitemaps import sitemaps

urlpatterns = [
    path("connexion/", views.LoginView.as_view(), name="short_code_login"),
    path("inscription/", views.SignupView.as_view(), name="signup"),
    path("connexion/code/", views.CodeLoginView.as_view(), name="check_short_code",),
    path("inscription/code/", views.CodeSignupView.as_view(), name="check_code_signup"),
    path("bienvenue/", views.TellMoreView.as_view(), name="tell_more"),
    path("deconnexion/", views.LogoutView.as_view(), name="disconnect"),
    path("offline", views.OfflineApp.as_view(), name="offline"),
    path("service-worker.js", (views.ServiceWorker.as_view()), name="sw.js"),
    path("rejoindre/", views.JoinView.as_view(), name="join"),
    path("intro/", views.IntroAppView.as_view(), name="intro"),
    path("choix-campagne/", views.ChooseCampaignView.as_view(), name="choose_campaign"),
    path("bienvenue/", views.WelcomeView.as_view(), name="welcome"),
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
    path(
        "groupes/<uuid:pk>/complet/",
        views.FullSupportGroupView.as_view(),
        name="full_group",
    ),
    path(
        "groupes/<uuid:pk>/agenda/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_events",
    ),
    path(
        "groupes/<uuid:pk>/comptes-rendus/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_reports",
    ),
    path(
        "groupes/<uuid:pk>/accueil/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_info",
    ),
    path(
        "groupes/<uuid:pk>/messages/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_messages",
    ),
    path(
        "groupes/<uuid:pk>/messages/<uuid:message_pk>/",
        views.SupportGroupMessageDetailView.as_view(),
        name="view_group_message",
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
    path("evenements/creer/", views.CreateEventView.as_view(), name="create_event"),
    path(
        "evenements/creer/<path>/",
        views.CreateEventView.as_view(),
        name="create_event_sub",
    ),
    path("evenements/<uuid:pk>/", views.EventDetailView.as_view(), name="view_event"),
    path("mes-groupes/", views.MyGroupsView.as_view(), name="list_my_groups"),
    path("navigation/", views.NavigationMenuView.as_view(), name="navigation_menu"),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
