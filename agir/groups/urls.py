from django.urls import path
from . import views

uuid = r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"
simple_id = r"[0-9]+"


urlpatterns = [
    # groups views
    path("groupes/creer/", views.CreateSupportGroupView.as_view(), name="create_group"),
    path(
        "groupes/creer/form/",
        views.PerformCreateSupportGroupView.as_view(),
        name="perform_create_group",
    ),
    path(
        "groupes/liste/", views.SupportGroupListView.as_view(), name="list_all_groups"
    ),
    path(
        "groupes/<uuid:pk>/", views.SupportGroupDetailView.as_view(), name="view_group"
    ),
    path(
        "groupes/<uuid:pk>/icalendar/",
        views.SupportGroupIcsView.as_view(),
        name="ics_group",
    ),
    path(
        "groupes/<uuid:pk>/manage/",
        views.SupportGroupManagementView.as_view(),
        name="manage_group",
    ),
    path(
        "groupes/<uuid:pk>/modifier/",
        views.ModifySupportGroupView.as_view(),
        name="edit_group",
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
        "groupes/retirer_gestionnaire/<int:pk>/",
        views.RemoveManagerView.as_view(),
        name="remove_manager",
    ),
    path(
        "livrets_thematiques/",
        views.ThematicBookletViews.as_view(),
        name="thematic_groups_list",
    ),
]
