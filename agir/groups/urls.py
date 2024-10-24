from django.urls import path, include
from django.views.generic import RedirectView

from . import views

uuid = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
simple_id = r"[0-9]+"

legacy_urlpatterns = [
    path(
        "groupes/<uuid:pk>/manage/",
        RedirectView.as_view(pattern_name="manage_group"),
        name="manage_group_legacy",
    ),
    path(
        "groupes/<uuid:pk>/modifier/",
        RedirectView.as_view(pattern_name="edit_group"),
        name="edit_group_legacy",
    ),
    path(
        "groupes/<uuid:pk>/gestion/informations/",
        views.SupportGroupManagementView.as_view(),
        name="manage_group",
    ),
    path(
        "groupes/<uuid:pk>/gestion/modifier/",
        views.SupportGroupManagementView.as_view(),
        name="edit_group",
    ),
]

api_urlpatterns = [
    path("", views.UserGroupsView.as_view(), name="api_user_groups"),
    path(
        "suggestions/",
        views.UserGroupSuggestionsView.as_view(),
        name="api_user_group_suggestions",
    ),
    path(
        "recherche/",
        views.GroupSearchAPIView.as_view(),
        name="api_group_search",
    ),
    path(
        "recherche/geo/",
        views.GroupLocationSearchAPIView.as_view(),
        name="api_group_location_search",
    ),
    path(
        "thematiques/",
        views.ThematicGroupsView.as_view(),
        name="api_thematic_groups",
    ),
    path(
        "sous-types/",
        views.GroupSubtypesView.as_view(),
        name="api_group_subtypes",
    ),
    path(
        "<uuid:pk>/",
        views.GroupDetailAPIView.as_view(),
        name="api_group_view",
    ),
    path(
        "<uuid:pk>/rejoindre/",
        views.JoinGroupAPIView.as_view(),
        name="api_group_join",
    ),
    path(
        "<uuid:pk>/suivre/",
        views.FollowGroupAPIView.as_view(),
        name="api_group_follow",
    ),
    path(
        "<uuid:pk>/quitter/",
        views.QuitGroupAPIView.as_view(),
        name="api_group_quit",
    ),
    path(
        "<uuid:pk>/suggestions/",
        views.NearGroupsAPIView.as_view(),
        name="api_near_groups_view",
    ),
    path(
        "<uuid:pk>/evenements/",
        views.GroupEventsAPIView.as_view(),
        name="api_group_events_view",
    ),
    path(
        "<uuid:pk>/evenements/passes/",
        views.GroupPastEventsAPIView.as_view(),
        name="api_group_past_events_view",
    ),
    path(
        "<uuid:pk>/evenements/a-venir/",
        views.GroupUpcomingEventsAPIView.as_view(),
        name="api_group_upcoming_events_view",
    ),
    path(
        "<uuid:pk>/evenements-rejoints/",
        views.GroupEventsJoinedAPIView.as_view(),
        name="api_group_joined_events_view",
    ),
    path(
        "<uuid:pk>/evenements/compte-rendus/",
        views.GroupPastEventReportsAPIView.as_view(),
        name="api_group_past_event_reports_view",
    ),
    path(
        "<uuid:pk>/messages/",
        views.GroupMessagesAPIView.as_view(),
        name="api_group_message_list",
    ),
    path(
        "<uuid:pk>/envoi-message-prive/",
        views.GroupMessagesPrivateAPIView.as_view(),
        name="api_send_private_group_message",
    ),
    path(
        "messages/<uuid:pk>/participants/",
        views.GroupMessageParticipantsAPIView.as_view(),
        name="api_group_message_participants",
    ),
    path(
        "messages/<uuid:pk>/",
        views.GroupSingleMessageAPIView.as_view(),
        name="api_group_message_detail",
    ),
    path(
        "messages/<uuid:pk>/comments/",
        views.GroupMessageCommentsAPIView.as_view(),
        name="api_group_message_comment_list",
    ),
    path(
        "messages/comments/<uuid:pk>/",
        views.GroupSingleCommentAPIView.as_view(),
        name="api_group_message_comment_detail",
    ),
    path(
        "messages/notification/<uuid:pk>/",
        views.GroupMessageNotificationStatusAPIView.as_view(),
        name="api_group_message_notification",
    ),
    path(
        "messages/verrouillage/<uuid:pk>/",
        views.GroupMessageLockedStatusAPIView.as_view(),
        name="api_group_message_locked",
    ),
    path(
        "<uuid:pk>/membres/",
        views.GroupMembersAPIView.as_view(),
        name="api_group_members",
    ),
    path(
        "membres/<int:pk>/",
        views.GroupMemberUpdateAPIView.as_view(),
        name="api_group_member_update",
    ),
    path(
        "membres/<int:pk>/informations/",
        views.MemberPersonalInformationAPIView.as_view(),
        name="api_group_member_details",
    ),
    path(
        "<uuid:pk>/update/",
        views.GroupUpdateAPIView.as_view(),
        name="api_group_general",
    ),
    path(
        "<uuid:pk>/invitation/",
        views.GroupInvitationAPIView.as_view(),
        name="api_group_invitation",
    ),
    path(
        "<uuid:pk>/finance/",
        views.GroupFinanceAPIView.as_view(),
        name="api_group_finance",
    ),
    path(
        "<uuid:pk>/link/",
        views.CreateSupportGroupExternalLinkAPIView.as_view(),
        name="api_group_link_create",
    ),
    path(
        "<uuid:group_pk>/link/<int:pk>/",
        views.RetrieveUpdateDestroySupportGroupExternalLinkAPIView.as_view(),
        name="api_group_link_retrieve_update_destroy",
    ),
    path(
        "<uuid:group_pk>/membre/",
        views.GroupUpdateOwnMembershipAPIView.as_view(),
        name="api_group_update_own_membership",
    ),
    path(
        "<uuid:pk>/stats/",
        views.GroupStatisticsAPIView.as_view(),
        name="api_group_statistics",
    ),
]

urlpatterns = [
    path("api/groupes/", include(api_urlpatterns)),
    # groups views
    path("", include(legacy_urlpatterns)),
    path("groupes/creer/", views.CreateSupportGroupView.as_view(), name="create_group"),
    path(
        "groupes/creer/form/",
        views.PerformCreateSupportGroupView.as_view(),
        name="perform_create_group",
    ),
    path("groupes/liste/", views.SupportGroupListView.as_view(), name="search_group"),
    path(
        "groupes/chercher/",
        views.LegacyGroupSearchAPIView.as_view(),
        name="legacy_api_search_group",
    ),
    path(
        "groupes/<uuid:pk>/icalendar/",
        views.SupportGroupIcsView.as_view(),
        name="legacy_ics_group",
    ),
    path(
        "groupes/<uuid:pk>/icalendar.ics",
        views.SupportGroupIcsView.as_view(),
        name="ics_group",
    ),
    path(
        "groupes/<uuid:pk>/gestion/transfert-de-membres/",
        views.TransferSupportGroupMembersView.as_view(),
        name="transfer_group_members",
    ),
    path(
        "groupes/<uuid:pk>/quitter/",
        views.QuitSupportGroupView.as_view(),
        name="quit_group",
    ),
    path(
        "groupes/<uuid:pk>/localisation/",
        views.ChangeGroupLocationView.as_view(),
        name="change_group_location",
    ),
    path(
        "groupes/<uuid:pk>/impression/",
        views.RedirectToPresseroView.as_view(),
        name="redirect_to_pressero",
    ),
    path(
        "groupes/retirer_gestionnaire/<int:pk>/",
        views.RemoveManagerView.as_view(),
        name="remove_manager",
    ),
    path(
        "livrets_thematiques/",
        RedirectView.as_view(pattern_name="thematic_groups"),
        name="thematic_groups_list",
    ),
    path(
        "groupes/invitation/",
        views.InvitationConfirmationView.as_view(),
        name="invitation_confirmation",
    ),
    path(
        "groupes/inscription/",
        views.InvitationWithSubscriptionView.as_view(),
        name="invitation_with_subscription_confirmation",
    ),
    path(
        "groupes/invitation/abus/",
        views.InvitationAbuseReportingView.as_view(),
        name="report_invitation_abuse",
    ),
    path(
        "groupes/<uuid:pk>/og-image/<str:cache_key>/",
        views.SuppportGroupOGImageView.as_view(),
        name="view_og_image_supportgroup",
    ),
    path(
        "groupes/<uuid:pk>/membres/liste.csv",
        views.DownloadMemberListView.as_view(),
        name="download_member_list",
    ),
    path(
        "groupes/<uuid:pk>/membres/emargement.pdf",
        views.DownloadAttendanceListView.as_view(),
        name="download_attendance_list",
    ),
]
