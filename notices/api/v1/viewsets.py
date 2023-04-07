from django.conf import settings
from django.shortcuts import get_object_or_404
from notices.models import Notification, Broadcast
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import DestroyModelMixin
from rest_framework_api_key.permissions import HasAPIKey
from push_notifications.api.rest_framework import (
    APNSDeviceViewSet,
    GCMDeviceViewSet,
    WebPushDeviceViewSet,
    WNSDeviceViewSet,
)
from apps.api.v1.permissions import IsOwner, HasApplicationAPIKey
from .serializers import (
    NotificationSerializer,
    BroadcastSerializer,
    ServerNotificationSerializer,
)
from ...models import Application


class ApplicationAuthorizedMixin:
    permission_classes = (
        IsAuthenticated,
        IsOwner,
    )

    def get_application(self):
        application = Application.get_from_request_headers(self.request)
        return application

    def get_queryset(self):
        application = self.get_application()
        # filter all devices to only those belonging to the current application user
        return self.queryset.filter(
            user=self.request.user, application_id=application.id
        )

    def perform_create(self, serializer):
        application = self.get_application()
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, application_id=application.id)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        application = self.get_application()
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, application_id=application.id)
        return super().perform_update(serializer)


class NotificationViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = NotificationSerializer

    def get_application(self):
        application = Application.get_from_request_headers(self.request)
        return application

    def get_queryset(self):
        application = self.get_application()
        queryset = super().get_queryset()
        return queryset.filter(recipient=self.request.user, application=application)

    @action(methods=["GET"], url_path="mark-all-as-read", detail=False)
    def mark_as_read_all(self, request, *args, **kwargs):
        self.request.user.notifications.mark_all_as_read()
        return Response(data={"message": "success"})

    @action(methods=["GET"], url_path="mark-as-read", detail=True)
    def mark_as_read(self, request, id, *args, **kwargs):
        notification = get_object_or_404(Notification, recipient=request.user, id=id)
        notification.mark_as_read()
        return Response(data={"message": "success"})

    @action(methods=["GET"], url_path="mark-as-unread", detail=True)
    def mark_as_unread(self, request, id, *args, **kwargs):
        notification = get_object_or_404(Notification, recipient=request.user, id=id)
        notification.mark_as_unread()
        return Response(data={"message": "success"})

    def perform_destroy(self, instance):
        if settings.get_config()["SOFT_DELETE"]:
            instance.deleted = True
            instance.save()
        else:
            instance.delete()
        return Response(data={"message": "success"})


class APNSDeviceAuthorizedViewSet(ApplicationAuthorizedMixin, APNSDeviceViewSet):
    pass


class GCMDeviceAuthorizedViewSet(ApplicationAuthorizedMixin, GCMDeviceViewSet):
    pass


class WebPushDeviceAuthorizedViewSet(ApplicationAuthorizedMixin, WebPushDeviceViewSet):
    pass


class WNSDeviceAuthorizedViewSet(ApplicationAuthorizedMixin, WNSDeviceViewSet):
    pass


class ServerNotificationViewSet(GenericViewSet):
    queryset = Notification.objects.all()
    permission_classes = [HasApplicationAPIKey]
    authentication_classes = []
    serializer_class = ServerNotificationSerializer

    def get_application(self):
        application = Application.get_from_request_headers(self.request)
        return application

    def get_queryset(self):
        application = self.get_application()
        return self.queryset.filter(application_id=application.id)

    @action(methods=["POST"], url_path="send", detail=False)
    def send_notifications(self, request, *args, **kwargs):
        """Send Notifications"""
        return Response(data={"message": "sending notifications"})


class ServerBroadcastViewSet(ReadOnlyModelViewSet):
    queryset = Broadcast.objects.all()
    serializer_class = BroadcastSerializer
    permission_classes = [HasApplicationAPIKey]

    def get_queryset(self):
        application = Application.get_from_request_headers(self.request)
        # filter all devices to only those belonging to the current application user
        return self.queryset.filter(application=application)
