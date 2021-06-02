from django.urls import path

from agir.msgs import views

urlpatterns = [
    path("api/report/", views.UserReportAPIView.as_view(), name="api_report",),
    path("api/user/messages/", views.UserMessagesAPIView.as_view(), name="api_report",),
]
