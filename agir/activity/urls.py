from django.urls import path

from . import views

app_name = "activity"

urlpatterns = [
    path("api/activity/<int:pk>", views.ActivityAPIView.as_view(), name="api_activity"),
]
