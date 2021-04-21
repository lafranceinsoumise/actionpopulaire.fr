from django.urls import path, include
from push_notifications.api.rest_framework import (
    WebPushDeviceAuthorizedViewSet,
    APNSDeviceAuthorizedViewSet,
)
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"webpush", WebPushDeviceAuthorizedViewSet)
router.register(r"apple", APNSDeviceAuthorizedViewSet)

urlpatterns = [
    path("api/device/", include(router.urls)),
    path(
        "api/notifications/subscriptions/",
        views.ListCreateDestroySubscriptionAPIView.as_view(),
    ),
]
