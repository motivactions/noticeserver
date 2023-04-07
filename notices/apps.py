from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NoticesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notices"
    label = "notices"
    verbose_name = _("Notices")
