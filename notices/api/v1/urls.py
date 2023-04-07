from .viewsets import (
    APNSDeviceAuthorizedViewSet,
    GCMDeviceAuthorizedViewSet,
    WebPushDeviceAuthorizedViewSet,
    WNSDeviceAuthorizedViewSet,
    ServerNotificationViewSet,
)
from rest_framework.routers import DefaultRouter

from notices.api.v1.viewsets import NotificationViewSet, ServerBroadcastViewSet

router = DefaultRouter()
router.register("apnsdevices", APNSDeviceAuthorizedViewSet, "apnsdevice")
router.register("gcmdevices", GCMDeviceAuthorizedViewSet, "gcmdevice")
router.register("webpushdevices", WebPushDeviceAuthorizedViewSet, "webpushdevice")
router.register("wnsdevices", WNSDeviceAuthorizedViewSet, "wnsdevice")
router.register("notifications", NotificationViewSet, "notification")
router.register("server/broadcasts", ServerBroadcastViewSet, "broadcast")
router.register("server/notifications", ServerNotificationViewSet, "admin_notification")

urlpatterns = [] + router.urls
