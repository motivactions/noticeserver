from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import Broadcast, Notification
from notifications.admin import AbstractNotificationAdmin


@admin.register(Broadcast)
class BroadcastModelAdmin(admin.ModelAdmin):
    menu_order = 9
    model = Broadcast
    menu_label = _("Broadcasts")
    list_display = ["title", "message", "sent_counter", "last_sent_at"]
    list_filter = ["last_sent_at"]
    actions = ["send"]

    @admin.action(description=_("Send selected Broadcast message"))
    def send(self, request, queryset):
        try:
            for obj in queryset:
                obj.send(actor=request.user)
            self.message_user(
                request,
                level=messages.SUCCESS,
                message=_("Notification #{} sent.").format(obj.id),
            )
        except Exception as err:
            self.message_user(request, level=messages.ERROR, message=err)


admin.site.unregister(Notification)


class NotificationModelAdmin(AbstractNotificationAdmin):
    search_fields = ["recipient__username"]
    list_filter = [
        "application",
        "level",
        "unread",
        "public",
        "timestamp",
        "notified_email",
        "notified_apns",
        "notified_gcm",
        "notified_wns",
        "notified_webpush",
    ]
    actions = [
        "send_email",
        "send_android",
        "send_apple",
        "send_windows",
        "send_webpush",
    ]

    @admin.action(description="Send selected notifications by email")
    def send_email(self, request, queryset):
        queryset.update(emailed=True)

    @admin.action(description="Send selected notifications to android devices")
    def send_android(self, request, queryset):
        queryset.update(notified_gcm=True)

    @admin.action(description="Send selected notifications to apple devices")
    def send_apple(self, request, queryset):
        queryset.update(notified_apns=True)

    @admin.action(description="Send selected notifications to windows devices")
    def send_windows(self, request, queryset):
        queryset.update(notified_wns=True)

    @admin.action(description="Send selected notifications to webpush / browser")
    def send_webpush(self, request, queryset):
        queryset.update(notified_webpush=True)


admin.site.register(Notification, NotificationModelAdmin)
