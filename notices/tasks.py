from django.apps import apps
from celery import shared_task
from .signals import bulk_notify

get_model = apps.get_model


@shared_task(name="notices.create_notification", bind=True)
def create_notification(self):
    bulk_notify.send()


@shared_task(name="notices.send_email_notification", bind=True)
def send_email_notification(self):
    pass


@shared_task(name="notices.send_push_notification", bind=True)
def send_push_notification(obj_id, app_label, model_name, recipients=None):
    pass
