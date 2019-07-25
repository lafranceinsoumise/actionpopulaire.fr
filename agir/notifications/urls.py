from django.urls import path

from agir.notifications import views

urlpatterns = [
    path(
        "notification/<int:pk>/",
        views.FollowNotificationView.as_view(),
        name="follow_notification",
    ),
    path(
        "notification/seen/",
        views.NotificationsSeenView.as_view(),
        name="notifications_seen",
    ),
    path("notification/liste", views.NotificationsView.as_view(), name="notifications"),
]
