from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path, include
from django.views.generic import RedirectView

from . import views
from ..front.sitemaps import sitemaps

supportgroup_settings_patterns = [
    path("gestion/", views.GroupSettingsView.as_view(), name="view_group_settings",),
    path(
        "gestion/membres/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_members",
    ),
    path(
        "gestion/animation/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_management",
    ),
    path(
        "gestion/finance/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_finance",
    ),
    path(
        "gestion/general/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_general",
    ),
    path(
        "gestion/localisation/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_location",
    ),
    path(
        "gestion/contact/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_contact",
    ),
    path(
        "gestion/liens/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_links",
    ),
    path(
        "gestion/materiel/",
        views.GroupSettingsView.as_view(),
        name="view_group_settings_materiel",
    ),
]

supportgroup_patterns = [
    path("", views.SupportGroupDetailView.as_view(), name="view_group"),
    path("complet/", views.FullSupportGroupView.as_view(), name="full_group",),
    path("agenda/", views.SupportGroupDetailView.as_view(), name="view_group_events",),
    path(
        "comptes-rendus/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_reports",
    ),
    path(
        "messages/", views.SupportGroupDetailView.as_view(), name="view_group_messages",
    ),
    path(
        "messages/<uuid:message_pk>/",
        views.SupportGroupMessageDetailView.as_view(),
        name="view_group_message",
    ),
    path("agenda/", include(supportgroup_settings_patterns)),
    path("comptes-rendus/", include(supportgroup_settings_patterns)),
    path("messages/", include(supportgroup_settings_patterns)),
    path("", include(supportgroup_settings_patterns)),
]

urlpatterns = [
    path("connexion/", views.LoginView.as_view(), name="short_code_login"),
    path("inscription/", views.SignupView.as_view(), name="signup"),
    path("connexion/code/", views.CodeLoginView.as_view(), name="check_short_code",),
    path("inscription/code/", views.CodeSignupView.as_view(), name="check_code_signup"),
    path("bienvenue/", views.TellMoreView.as_view(), name="tell_more"),
    path("deconnexion/", views.LogoutView.as_view(), name="disconnect"),
    path("offline", views.OfflineApp.as_view(), name="offline"),
    path("sw.js", (views.ServiceWorker.as_view()), name="sw.js"),
    path("rejoindre/", RedirectView.as_view(pattern_name="signup"), name="join"),
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
    path("groupes/<uuid:pk>/", include(supportgroup_patterns)),
    path("activite/", views.ActivityView.as_view(), name="list_activities",),
    path(
        "activite/parametres/",
        views.NotificationSettingsView.as_view(),
        name="list_activities.notification_settings",
    ),
    path(
        "a-traiter/",
        RedirectView.as_view(pattern_name="list_activities", permanent=True),
        name="list_required_activities",
    ),
    path(
        "a-traiter/parametres/",
        RedirectView.as_view(
            pattern_name="list_activities.notification_settings", permanent=True
        ),
        name="list_required_activities.notification_settings",
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
        "evenements/<uuid:pk>/parametres/",
        views.EventSettingsView.as_view(),
        name="view_event_settings",
    ),
    path(
        "evenements/creer/<path>/",
        views.CreateEventView.as_view(),
        name="create_event_sub",
    ),
    path("evenements/<uuid:pk>/", views.EventDetailView.as_view(), name="view_event"),
    path("mes-groupes/", views.MyGroupsView.as_view(), name="list_my_groups"),
    path("navigation/", views.NavigationMenuView.as_view(), name="navigation_menu"),
    path("messages/", views.UserMessagesView.as_view(), name="user_messages"),
    path(
        "messages/<uuid:pk>/",
        views.UserMessagesView.as_view(),
        name="user_message_details",
    ),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
