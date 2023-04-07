from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags import humanize

from notices.models import (
    Notification,
    Broadcast,
    ActionObjectSerializer,
    TargetObjectSerializer,
)
from rest_framework import serializers


class ContentTypeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = "__all__"

    def get_name(self, obj) -> str:
        return f"{obj.app_label}.{obj.model}"


class NotificationSerializer(serializers.ModelSerializer):
    actor_content_type = ContentTypeSerializer()
    actor_object_id = serializers.UUIDField()
    target = ActionObjectSerializer()
    action = TargetObjectSerializer()
    data = serializers.JSONField()
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Notification
        exclude = ["application"]

    def validate(self, attrs):
        return super().validate(attrs)

    def get_humanize_time(self, obj) -> str:
        return humanize.naturaltime(obj.timestamp)


class ServerNotificationSerializer(serializers.ModelSerializer):
    actor_content_type = ContentTypeSerializer()
    actor_object_id = serializers.UUIDField()
    target = ActionObjectSerializer()
    action = TargetObjectSerializer()
    data = serializers.JSONField()
    humanize_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Notification
        fields = "__all__"

    def validate(self, attrs):
        return super().validate(attrs)

    def get_humanize_time(self, obj) -> str:
        return humanize.naturaltime(obj.timestamp)


class BroadcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broadcast
        fields = "__all__"
