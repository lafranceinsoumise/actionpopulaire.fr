from django.conf import settings
from django.contrib.sitemaps.views import sitemap, index as sitemap_index
from django.urls import reverse_lazy, path, re_path, include
from django.views.generic import RedirectView

from . import views
from . import api_views
from ..front.sitemaps import sitemaps

supportgroup_settings_patterns = [
    path(
        "gestion/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings",
    ),
    path(
        "gestion/membres/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_members",
    ),
    path(
        "gestion/contacts/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_followers",
    ),
    path(
        "gestion/animation/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_management",
    ),
    path(
        "gestion/finance/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_finance",
    ),
    path(
        "gestion/general/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_general",
    ),
    path(
        "gestion/localisation/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_location",
    ),
    path(
        "gestion/contact/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_contact",
    ),
    path(
        "gestion/liens/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_links",
    ),
    path(
        "gestion/materiel/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_materiel",
    ),
    path(
        "gestion/certification/",
        views.SupportGroupSettingsView.as_view(),
        name="view_group_settings_certification",
    ),
]

supportgroup_patterns = [
    path("", views.SupportGroupDetailView.as_view(), name="view_group"),
    path(
        "complet/",
        views.BaseAppSoftAuthView.as_view(),
        name="full_group",
    ),
    path(
        "agenda/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_events",
    ),
    path(
        "comptes-rendus/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_reports",
    ),
    path(
        "messages/",
        views.SupportGroupDetailView.as_view(),
        name="view_group_messages",
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
    path(
        "gestion/",
        views.EventSettingsView.as_view(),
        name="view_event_settings",
    ),
    path(
        "gestion/general/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_general",
    ),
    path(
        "gestion/participants/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_members",
    ),
    path(
        "gestion/organisation/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_organisation",
    ),
    path(
        "gestion/droits/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_rights",
    ),
    path(
        "gestion/video-conference/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_video",
    ),
    path(
        "gestion/contact/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_contact",
    ),
    path(
        "gestion/localisation/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_location",
    ),
    path(
        "gestion/compte-rendu/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_feedback",
    ),
    path(
        "gestion/annuler/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_cancel",
    ),
    path(
        "gestion/documents/",
        views.EventSettingsView.as_view(),
        name="view_event_settings_required_documents",
    ),
    path(
        "documents/",
        views.EventProjectView.as_view(),
        name="event_project",
    ),
]

voting_proxy_patterns = [
    path(
        "donner-ma-procuration/",
        views.VotingProxyRequestView.as_view(),
        name="new_voting_proxy_request",
    ),
    path(
        "reponse/",
        views.VotingProxyRequestView.as_view(),
        name="voting_proxy_request_details",
    ),
    path(
        "prendre-une-procuration/",
        views.VotingProxyView.as_view(),
        name="new_voting_proxy",
    ),
    path(
        "prendre-une-procuration/<uuid:pk>/",
        views.VotingProxyView.as_view(),
        name="reply_to_voting_proxy_requests",
    ),
    path(
        "prendre-une-procuration/<uuid:pk>/demandes/",
        views.VotingProxyView.as_view(),
        name="accepted_voting_proxy_requests",
    ),
]

urlpatterns = [
    ## APP & AUTH VIEWS
    path("connexion/", views.LoginView.as_view(), name="short_code_login"),
    path("inscription/", views.SignupView.as_view(), name="signup"),
    path("rejoindre/", RedirectView.as_view(pattern_name="signup"), name="join"),
    path(
        "connexion/code/",
        views.CodeLoginView.as_view(),
        name="check_short_code",
    ),
    path("inscription/code/", views.CodeSignupView.as_view(), name="check_code_signup"),
    path("deconnexion/", views.LogoutView.as_view(), name="disconnect"),
    path("bienvenue/", views.BaseAppCachedView.as_view(), name="tell_more"),
    path("404/", views.NotFoundView.as_view()),
    path("500/", views.BaseAppCachedView.as_view()),
    path("offline", views.BaseAppCachedView.as_view(), name="offline"),
    path("sw.js", (views.ServiceWorker.as_view()), name="sw.js"),
    path("sitemap.xml", sitemap_index, {"sitemaps": sitemaps}),
    path(
        "sitemap-<section>.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    ## DASHBOARD VIEWS
    path(
        "",
        views.HomepageView.as_view(),
        name="dashboard",
    ),
    path(
        "evenements/",
        RedirectView.as_view(pattern_name="dashboard"),
        name="list_events",
    ),
    path(
        "recherche/",
        views.SearchView.as_view(),
        name="search",
    ),
    path(
        "recherche/evenements/",
        views.SearchView.as_view(),
        name="search_events",
    ),
    path(
        "recherche/groupes/",
        views.SearchView.as_view(),
        name="search_groups",
    ),
    path(
        "api/recherche/",
        api_views.SearchSupportGroupsAndEventsAPIView.as_view(),
        name="api_search_supportgroup_and_events",
    ),
    path("mes-groupes/", views.UserSupportGroupsView.as_view(), name="list_my_groups"),
    path(
        "activite/",
        views.BaseAppSoftAuthView.as_view(),
        name="list_activities",
    ),
    path(
        "activite/parametres/",
        views.BaseAppHardAuthView.as_view(),
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
    path("messages/", views.UserMessagesView.as_view(), name="user_messages"),
    path(
        "messages/parametres/",
        views.UserMessagesView.as_view(),
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
    path(
        "agir/",
        views.BaseAppSoftAuthView.as_view(),
        name="tools",
    ),
    path("outils/", views.RedirectView.as_view(pattern_name="tools", permanent=True)),
    path("navigation/", views.BaseAppSoftAuthView.as_view(), name="navigation_menu"),
    ## EVENT VIEWS
    path("evenements/carte/", views.BaseAppCachedView.as_view(), name="event_map_page"),
    path("evenements/creer/", views.CreateEventView.as_view(), name="create_event"),
    path(
        "evenements/creer/<path>/",
        views.CreateEventView.as_view(),
        name="create_event_sub",
    ),
    path("evenements/<uuid:pk>/", include(event_settings_patterns)),
    path(
        "evenements/documents-justificatifs/",
        views.BaseAppSoftAuthView.as_view(),
        name="event_required_documents",
    ),
    path(
        "documents-justificatifs/",
        views.BaseAppSoftAuthView.as_view(),
        name="event_required_documents_modal",
    ),
    path(
        "toktok/",
        views.BaseAppSoftAuthView.as_view(),
        name="toktok_preview",
    ),
    ## SUPPORTGROUP VIEWS
    path(
        "groupes/",
        RedirectView.as_view(url=reverse_lazy("dashboard")),
        name="list_groups",
    ),
    path("groupes/carte/", views.BaseAppCachedView.as_view(), name="group_map_page"),
    path("groupes/<uuid:pk>/", include(supportgroup_patterns)),
    ## CONTACT VIEWS
    path("contacts/creer/", views.BaseAppSoftAuthView.as_view(), name="create_contact"),
    path(
        "contacts/creer/valider/",
        RedirectView.as_view(pattern_name="create_contact", permanent=True),
        name="create_contact_validation",
    ),
    path(
        "contacts/creer/succes/",
        RedirectView.as_view(pattern_name="create_contact", permanent=True),
        name="create_contact_success",
    ),
    # DONATION VIEWS
    path(
        "dons/",
        views.DonationView.as_view(),
        name="donation_amount",
    ),
    path(
        "dons/infos/",
        views.DonationView.as_view(),
        name="donation_information_modal",
    ),
    path(
        "dons/informations/",
        views.DonationView.as_view(),
        name="donation_information",
    ),
    path(
        "dons-mensuels/informations/",
        views.DonationView.as_view(),
        name="monthly_donation_information",
    ),
    path(
        "2022/dons/",
        RedirectView.as_view(
            pattern_name="donation_amount", permanent=True, query_string=True
        ),
        name="donations_2022_amount",
    ),
    path(
        "2022/dons/infos/",
        RedirectView.as_view(
            pattern_name="donation_information_modal", permanent=True, query_string=True
        ),
        name="donation_2022_information_modal",
    ),
    path(
        "2022/dons/informations/",
        RedirectView.as_view(
            pattern_name="donation_information", permanent=True, query_string=True
        ),
        name="donation_2022_information",
    ),
    path(
        "2022/dons-mensuels/informations/",
        RedirectView.as_view(
            pattern_name="monthly_donation_information",
            permanent=True,
            query_string=True,
        ),
        name="monthly_donation_2022_information",
    ),
    # VOTING PROXIES
    path("procuration/", include(voting_proxy_patterns)),
    # POLLING STATION OFFICERS
    path("elections/assesseures-deleguees/", views.PollingStationOfficerView.as_view()),
    path("404/", views.NotFoundView.as_view()),
    ## REDIRECT / EXTERNAL VIEWS
    path("nsp/", views.NSPView.as_view(), name="nsp"),
    path("nsp/referral/", views.NSPReferralView.as_view(), name="nsp_referral"),
    # https://lafranceinsoumise.fr/
    path("homepage/", RedirectView.as_view(url=settings.MAIN_DOMAIN), name="homepage"),
    # old urls
    re_path("^old(.*)$", views.NBUrlsView.as_view(), name="old_urls"),
]
