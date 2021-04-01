from django.urls import path, include
from push_notifications.api.rest_framework import WebPushDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"webpush", WebPushDeviceAuthorizedViewSet)

urlpatterns = [
    path("api/device/", include(router.urls)),
]
