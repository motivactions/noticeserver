import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mass_mail
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # NOQA
from django.template.loader import render_to_string
from notifications.base.models import NotificationQuerySet, id2slug
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from rest_framework_api_key.models import APIKey
from rest_framework import serializers
from push_notifications.models import GCMDevice, APNSDevice, WebPushDevice, WNSDevice
from apps.models import Application


from swapper import load_model

from .signals import bulk_notify, firebase_push_notify

DEVICE_MODEL = {
    "Google": GCMDevice,
    "Firebase": GCMDevice,
    "Apple": APNSDevice,
    "Windows": WNSDevice,
    "Webpush": WebPushDevice,
}

User = get_user_model()


class ActionObjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120, required=True)
    description = serializers.CharField(max_length=255, required=True)
    image = serializers.URLField(required=False)
    url = serializers.URLField(required=False)


class TargetObjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120, required=True)
    description = serializers.CharField(max_length=255, required=True)
    image = serializers.URLField(required=False)
    url = serializers.URLField(required=False)


class ApplicationPlatform(models.Model):
    FIREBASE = "FCM"
    APPLE = "APNS"
    GOOGLE = "GCM"
    WINDOWS = "WNS"
    WEBPUSH = "WP"
    PLATFORMS = [
        (FIREBASE, "Firebase"),
        (APPLE, "Apple"),
        (GOOGLE, "Google"),
        (WINDOWS, "Windows"),
        (WEBPUSH, "Web Push"),
    ]
    application = models.ForeignKey(
        Application,
        related_name="platforms",
        on_delete=models.CASCADE,
    )
    platform = models.CharField(
        max_length=5,
        choices=PLATFORMS,
        default=FIREBASE,
        verbose_name=_("Platform"),
        db_index=True,
    )
    configs = models.JSONField(null=False, blank=False, verbose_name=_("Configs"))

    def __str__(self) -> str:
        return f"{self.application}"


class NotificationPreference(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notice_preferences",
        verbose_name=_("User"),
    )

    email = models.BooleanField(
        default=True,
        help_text=_("Receive notification by email"),
    )
    push_notification = models.BooleanField(
        default=True,
        help_text=_("Receive notification by app"),
    )

    # Notification settings
    article_notification = models.BooleanField(
        default=True,
        verbose_name=_("Article Notice"),
        help_text=_("Receive article notification"),
    )

    class Meta:
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        return f"{self.user}"


class Notification(models.Model):
    SUCCESS, INFO, WARNING, PROMOTION, ERROR = (
        "success",
        "info",
        "warning",
        "promotion",
        "error",
    )
    LEVELS = (
        (SUCCESS, _("Success")),
        (INFO, _("Info")),
        (WARNING, _("Warning")),
        (PROMOTION, _("Promotion")),
        (ERROR, _("Error")),
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    level = models.CharField(
        choices=LEVELS,
        default=INFO,
        max_length=20,
    )
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    recipient = models.ForeignKey(
        User,
        blank=False,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    actor_content_type = models.ForeignKey(
        ContentType,
        related_name="notify_actor",
        on_delete=models.CASCADE,
    )
    actor_object_id = models.CharField(max_length=255)
    actor = GenericForeignKey("actor_content_type", "actor_object_id")

    verb = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target = models.JSONField(blank=True, null=True)
    action = models.JSONField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)

    # Status Fields
    unread = models.BooleanField(default=True, blank=False, db_index=True)
    public = models.BooleanField(default=True, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    notified_email = models.BooleanField(default=False, db_index=True)
    notified_apns = models.BooleanField(default=False, db_index=True)
    notified_gcm = models.BooleanField(default=False, db_index=True)
    notified_wns = models.BooleanField(default=False, db_index=True)
    notified_webpush = models.BooleanField(default=False, db_index=True)
    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ("-timestamp",)
        index_together = ("recipient", "unread")

    def timesince(self, now=None):
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """
        from django.utils.timesince import timesince as timesince_

        return timesince_(self.timestamp, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def clean(self):
        # Validate target data
        # from rest_framework.exceptions import ValidationError

        if self.target is not None:
            try:
                target = TargetObjectSerializer(data=self.target)
                target.is_valid(raise_exception=True)
                self.target = target.data
            except Exception as err:
                raise ValidationError(
                    {
                        "target": [
                            f"{key} - {', '.join([str(v) for v in val]).lower()}"
                            for key, val in err.detail.items()
                        ]
                    }
                )

        # validate action data
        if self.action is not None:
            try:
                action = ActionObjectSerializer(data=self.action)
                action.is_valid(raise_exception=True)
                self.action = action.data
            except Exception as err:
                raise ValidationError(
                    {
                        "action": [
                            f"{key} - {', '.join([str(v) for v in val]).lower()}"
                            for key, val in err.detail.items()
                        ]
                    }
                )

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Broadcast(models.Model):
    EMAIL = "email"
    NOTIFICATION = "notification"
    ANDROID_NOTIFICATION = "android_notification"
    APPLE_NOTIFICATION = "apple_notification"
    ALL_MEDIA = "all"

    MEDIA_CHOICES = (
        (NOTIFICATION, _("Notification")),
        (EMAIL, _("Email")),
        (ANDROID_NOTIFICATION, _("Android Notification")),
        (ALL_MEDIA, _("All")),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        null=True,
        blank=True,
    )
    image = models.ImageField(
        null=True,
        blank=True,
        verbose_name=_("image"),
        help_text=_(
            "Make sure your image size atleast 1366x768px and 72 DPI resolution."
        ),
    )
    message = models.TextField(
        verbose_name=_("Message"),
        null=True,
        blank=True,
    )
    action_url = models.URLField(
        verbose_name=_("Action URL"),
    )
    action_title = models.CharField(
        max_length=255,
        verbose_name=_("Action Title"),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("created at"),
    )
    last_sent_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("last sent"),
    )
    sent_counter = models.IntegerField(
        default=0,
        editable=False,
        verbose_name=_("Counter"),
    )
    media = models.CharField(
        max_length=255,
        default=NOTIFICATION,
        choices=MEDIA_CHOICES,
        verbose_name=_("media"),
    )

    users = models.ManyToManyField(
        User,
        blank=True,
        related_name="broadcasts",
        verbose_name=_("user"),
        help_text=_("Recipients"),
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="broadcasts",
        verbose_name=_("group"),
        help_text=_("Group of recipients"),
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="broadcasts",
    )

    class Meta:
        verbose_name = _("Broadcast")
        verbose_name_plural = _("Broadcasts")

    def __str__(self):
        return f"{self.title}"

    def _send_notification(self, actor, recipients, data):
        bulk_notify.send(
            self,
            actor=actor,
            verb="broadcast",
            recipients=recipients,
            application=self.application,
            **data,
        )

    def _send_firebase(self, recipients, data):
        firebase_push_notify.send(
            self,
            recipients=recipients,
            title=self.title,
            message=self.message,
            data=data,
        )

    def _send_email(self, recipients, data):
        # TODO find more eficient way to send mas email
        from django.conf import settings

        sender_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "My Domain <noreply@mydomain.com>",
        )

        recipient_emails = [
            user.email for user in recipients if user.email not in ["", None]
        ]
        email_content = render_to_string(
            template_name="notices/email_broadcast.txt",
            context={
                "title": self.title,
                "message": self.message,
                "data": data,
            },
        )
        messages = [(self.title, email_content, sender_email, recipient_emails)]
        send_mass_mail(messages)

    def get_title(self):
        return self.title

    def get_message(self):
        return self.message

    def get_data(self):
        data = {
            "type": "broadcast",
            "title": self.title,
            "message": self.message,
            "actions": {
                "url": self.action_url,
                "title": self.action_title,
            },
        }
        if bool(self.image):
            data["image"] = {
                "url": self.image.url,
                "width": self.image.width,
                "height": self.image.height,
            }
        return data

    def get_recipients(self):
        queryset = User.objects.filter(is_active=True)
        user_ids = [user.id for user in self.users.all()]
        group_query = models.Q(groups__in=self.groups.all())
        user_query = models.Q(id__in=user_ids)
        queryset = queryset.filter(group_query | user_query)
        return queryset

    def send(self, actor=None, **kwargs):
        recipients = self.get_recipients()

        # Get dictionary extra data
        data = self.get_data()
        data.update(kwargs)

        # Send web notification
        if self.media == self.EMAIL:
            self._send_email(recipients, data)
        elif self.media == self.ANDROID_NOTIFICATION:
            self._send_firebase(recipients, data)
        elif self.media == self.NOTIFICATION:
            self._send_notification(actor, recipients, data)
        elif self.media == self.ALL_MEDIA:
            self._send_email(recipients, data)
            self._send_firebase(recipients, data)
            self._send_notification(actor, recipients, data)
        else:
            return
        self.sent_counter += 1
        self.last_sent_at = timezone.now()
        self.save()


def bulk_notification_handler(verb, **kwargs):
    """
    Handler function to bulk create Notification instance upon action signal call.
    """

    EXTRA_DATA = True

    # Pull the options out of kwargs
    kwargs.pop("signal", None)
    kwargs.pop("sender")
    recipient = kwargs.pop("recipients")
    actor = kwargs.pop("actor")

    if actor is None:
        actor = User.objects.filter(is_superuser=True).first()

    optional_objs = [
        (kwargs.pop(opt, None), opt) for opt in ("target", "action_object")
    ]
    public = bool(kwargs.pop("public", True))
    description = kwargs.pop("description", None)
    timestamp = kwargs.pop("timestamp", timezone.now())
    Notification = load_model("notifications", "Notification")
    level = kwargs.pop("level", Notification.LEVELS.info)
    application = kwargs.pop("application", None)

    # Check if User or Group
    if isinstance(recipient, Group):
        recipients = recipient.user_set.all()
    elif isinstance(recipient, (QuerySet, list)):
        recipients = recipient
    else:
        recipients = [recipient]

    new_notifications = []

    for recipient in recipients:
        newnotify = Notification(
            recipient=recipient,
            actor_content_type=ContentType.objects.get_for_model(actor),
            actor_object_id=actor.pk,
            verb=str(verb),
            public=public,
            description=description,
            timestamp=timestamp,
            application=application,
            level=level,
        )

        # Set optional objects
        for obj, opt in optional_objs:
            if obj is not None:
                setattr(newnotify, "%s_object_id" % opt, obj.pk)
                setattr(
                    newnotify,
                    "%s_content_type" % opt,
                    ContentType.objects.get_for_model(obj),
                )

        # extra data as json data
        if kwargs and EXTRA_DATA:
            newnotify.data = kwargs

        new_notifications.append(newnotify)

    results = Notification.objects.bulk_create(new_notifications)
    return results


def firebase_notification_handler(recipients, title, message, **kwargs):
    kwargs.pop("signal", None)
    kwargs.pop("sender", None)
    GCMDevice = apps.get_model("push_notifications.GCMDevice")
    recipient_ids = [user.id for user in recipients]
    gcm_devices = GCMDevice.objects.filter(user_id__in=recipient_ids, active=True)

    try:
        gcm_devices.send_message(message, title=title, payload=kwargs)
    except Exception as err:
        print(err)


# Connect the signal
bulk_notify.connect(
    bulk_notification_handler, dispatch_uid="notifications.models.notification"
)


firebase_push_notify.connect(
    firebase_notification_handler, dispatch_uid="push_notification.gcm.firebase"
)
