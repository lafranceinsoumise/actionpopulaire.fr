from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path, include
from django.views.generic import RedirectView

from . import views
from ..front.sitemaps import sitemaps

supportgroup_settings_patterns = [
    path("gestion/", views.BaseAppHardAuthView.as_view(), name="view_group_settings",),
    path(
        "gestion/membres/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_members",
    ),
    path(
        "gestion/contacts/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_contacts",
    ),
    path(
        "gestion/animation/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_management",
    ),
    path(
        "gestion/finance/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_finance",
    ),
    path(
        "gestion/general/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_general",
    ),
    path(
        "gestion/localisation/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_location",
    ),
    path(
        "gestion/contact/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_contact",
    ),
    path(
        "gestion/liens/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_links",
    ),
    path(
        "gestion/materiel/",
        views.BaseAppHardAuthView.as_view(),
        name="view_group_settings_materiel",
    ),
]

supportgroup_patterns = [
    path("", views.SupportGroupDetailView.as_view(), name="view_group"),
    path("complet/", views.BaseAppSoftAuthView.as_view(), name="full_group",),
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
        "message/<uuid:message_pk>/",
        views.BaseAppSoftAuthView.as_view(),
        name="view_group_message",
    ),
    path("agenda/", include(supportgroup_settings_patterns)),
    path("comptes-rendus/", include(supportgroup_settings_patterns)),
    path("messages/", include(supportgroup_settings_patterns)),
    path("", include(supportgroup_settings_patterns)),
]

event_settings_patterns = [
    path("", views.EventDetailView.as_view(), name="view_event"),
    path("gestion/", views.BaseAppHardAuthView.as_view(), name="view_event_settings",),
    path(
        "gestion/general/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_general",
    ),
    path(
        "gestion/participants/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_members",
    ),
    path(
        "gestion/organisation/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_organisation",
    ),
    path(
        "gestion/droits/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_rights",
    ),
    path(
        "gestion/video-conference/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_video",
    ),
    path(
        "gestion/contact/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_contact",
    ),
    path(
        "gestion/localisation/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_location",
    ),
    path(
        "gestion/compte-rendu/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_feedback",
    ),
    path(
        "gestion/annuler/",
        views.BaseAppHardAuthView.as_view(),
        name="view_event_settings_cancel",
    ),
]

urlpatterns = [
    path("connexion/", views.LoginView.as_view(), name="short_code_login"),
    path("inscription/", views.SignupView.as_view(), name="signup"),
    path("connexion/code/", views.CodeLoginView.as_view(), name="check_short_code",),
    path("inscription/code/", views.CodeSignupView.as_view(), name="check_code_signup"),
    path("deconnexion/", views.LogoutView.as_view(), name="disconnect"),
    path("bienvenue/", views.BaseAppCachedView.as_view(), name="tell_more"),
    path("offline", views.BaseAppCachedView.as_view(), name="offline"),
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
    path("groupes/carte/", views.BaseAppCachedView.as_view(), name="group_map_page"),
    path("groupes/<uuid:pk>/", include(supportgroup_patterns)),
    path("activite/", views.BaseAppSoftAuthView.as_view(), name="list_activities",),
    path(
        "activite/parametres/",
        views.BaseAppHardAuthView.as_view(),
        name="list_activities.notification_settings",
    ),
    path("outils/", views.BaseAppSoftAuthView.as_view(), name="tools",),
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
    path("", views.BaseAppCachedView.as_view(), name="dashboard",),
    path(
        "evenements/",
        RedirectView.as_view(pattern_name="dashboard"),
        name="list_events",
    ),
    path("evenements/carte/", views.BaseAppCachedView.as_view(), name="event_map_page"),
    path("evenements/creer/", views.BaseAppSoftAuthView.as_view(), name="create_event"),
    path(
        "documents-justificatifs/",
        views.BaseAppSoftAuthView.as_view(),
        name="event_required_documents_modal",
    ),
    path(
        "evenements/creer/<path>/",
        views.BaseAppSoftAuthView.as_view(),
        name="create_event_sub",
    ),
    path("evenements/<uuid:pk>/", include(event_settings_patterns)),
    path(
        "evenements/documents-justificatifs/",
        views.BaseAppSoftAuthView.as_view(),
        name="event_required_documents",
    ),
    path("evenements/<uuid:pk>/", views.EventDetailView.as_view(), name="view_event"),
    path(
        "evenements/<uuid:pk>/documents/",
        views.EventProjectView.as_view(),
        name="event_project",
    ),
    path("mes-groupes/", views.BaseAppSoftAuthView.as_view(), name="list_my_groups"),
    path("navigation/", views.BaseAppSoftAuthView.as_view(), name="navigation_menu"),
    path("messages/", views.BaseAppHardAuthView.as_view(), name="user_messages"),
    path(
        "messages/parametres/",
        views.BaseAppHardAuthView.as_view(),
        name="user_messages.notification_settings",
    ),
    path(
        "messages/<uuid:pk>/",
        views.UserMessageView.as_view(),
        name="user_message_details",
    ),
    path(
        "messages/<uuid:pk>/parametres/",
        views.UserMessageView.as_view(),
        name="user_message_details.notification_settings",
    ),
    path("contacts/creer/", views.BaseAppSoftAuthView.as_view(), name="create_contact"),
    path("dons/", views.DonationView.as_view(), name="donation_amount",),
    path("2022/dons/", views.Donation2022View.as_view(), name="donations_2022_amount",),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
