from django.urls import path

from . import views

app_name = "activity"

urlpatterns = [
    path(
        "api/activity/bulk/update-status/",
        views.ActivityStatusUpdateView.as_view(),
        name="api_activity_update_status",
    ),
    path(
        "api/activity/<int:pk>/", views.ActivityAPIView.as_view(), name="api_activity"
    ),
    path(
        "api/user/required-activities/",
        views.UserRequiredActivitiesAPIView.as_view(),
        name="api_user_required_activities",
    ),
    path(
        "api/user/activities/",
        views.UserActivitiesAPIView.as_view(),
        name="api_user_activities",
    ),
    path(
        "activite/<uuid:pk>/lien/",
        views.AnnouncementLinkView.as_view(),
        name="announcement_link",
    ),
]
