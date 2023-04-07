import os
from pathlib import Path
from .environ import env

DEBUG = True

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8001")

PROJECT_NAME = "Notice Server"

PROJECT_DIR = BASE_DIR / "server"

SECRET_KEY = "django-insecure-b(j+w&tmv6cq2&ufdo=@4(35-5qag-ahi6(gw(d^oaednfdo(h"

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://notices.dev-tunnel.mitija.com",
]

INSTALLED_APPS = [
    "apps",
    "auths",
    "notifications",
    "notices",
    "providers.authentics",
    "providers.authentics.api",
    # Dependencies
    "push_notifications",
    "easy_thumbnails",
    "rest_framework",
    "rest_framework_api_key",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    # Django
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Authentication
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "django_cleanup",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"


##############################################################################
# DATABASE
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
##############################################################################

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

##############################################################################
# QUEUES
##############################################################################

REDIS_SSL = env("REDIS_SSL", bool, False)

# save Celery task results in Django's database
CELERY_RESULT_BACKEND = "django-db"

# This configures Redis as the datastore between Django + Celery
CELERY_BROKER_URL = env("CELERY_BROKER_REDIS_URL")
# if you out to use os.environ the config is:
# CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_REDIS_URL', 'redis://localhost:6379')

CELERY_RESULT_EXTENDED = True

# this allows you to schedule items in the Django admin.
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"


##############################################################################
# AUTHENTICATIONS
##############################################################################


AUTHENTICS_BASEURL = "https://oauth2.dev-tunnel.mitija.com"

# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    "authentics": {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        "APP": {
            "client_id": "p09nQOLOf2HdOnz20N3kaU951hIBy7BaeLtwuRgQ",
            "secret": "sFkW2I337wddbF97unLoue3A7PZ3hrCF4joLUVtBgEupom634bpIW0FhKQ7dkQlhzlWqk1ptXgSNKi8soHxx3HXigyEWQOmjKILUOk16lxqihEg5088nKf1mlmKhVI9Y",
            "key": "",
        }
    }
}

# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_USER_MODEL = "auths.User"
AUTH_VALIDATORS = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": AUTH_VALIDATORS + "UserAttributeSimilarityValidator"},
    {"NAME": AUTH_VALIDATORS + "MinimumLengthValidator"},
    {"NAME": AUTH_VALIDATORS + "CommonPasswordValidator"},
    {"NAME": AUTH_VALIDATORS + "NumericPasswordValidator"},
]

# Authentication Service
AUTHENTICS_API_KEY = os.getenv("AUTHENTICS_API_KEY", "")
AUTHENTICS_CLIENT_ID = os.getenv("AUTHENTICS_CLIENT_ID", "")
AUTHENTICS_CLIENT_SECRET = os.getenv("AUTHENTICS_CLIENT_SECRET", "")
AUTHENTICS_REDIRECT_URL = os.getenv("AUTHENTICS_REDIRECT_URL", "")
AUTHENTICS_API_URL = os.getenv("AUTHENTICS_API_URL", "")

##############################################################################
# NOTIFICATIONS
##############################################################################

NOTIFICATIONS_NOTIFICATION_MODEL = "notices.Notification"

##############################################################################
# INTERNATIONALIZATION
# https://docs.djangoproject.com/en/4.0/topics/i18n/
##############################################################################

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_L10N = True
USE_TZ = True

##############################################################################
# STATICFILE & STORAGE
##############################################################################

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
MEDIA_URL = "/media/"

##############################################################################
# EMAIL
##############################################################################

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


##############################################################################
# PUSH Notification Settings
##############################################################################

WEB_PUSH_SERVER_KEY = ""  # NOQA

PUSH_NOTIFICATIONS_SETTINGS = {
    "CONFIG": "push_notifications.conf.AppConfig",
    "APPLICATIONS": {
        "39cdcae8-ea2e-4305-9a75-c37c3c0dad12": {
            "PLATFORM": "FCM",
            # "API_KEY": "AAAA3B09Grs:APA91bFn-x6a7wdioD6S8Ohn4gVVs8gHBXBExHpxzHWVZu85Su-u8gaElRugyXwcgRgigxQveZVOoAqGGyyZi270xZih2YAjVCjuFM0BIrZsG1Sjo_PnneRnqxTvIEnp20DjhhTdKDM5",  # NOQA
            "API_KEY": "AAAApTTMlFA:APA91bHr20m_9nSyWnqHzmS3ZonjeaHglvu0YSTTHkhT9FHgkF89GAsgIMxL7LSRVyImL3Sro2s2w3BKo7LcJ_QGUNLH7ZM57grRfkkzow1UKidRzO3q0SCDuLRtC6XFNAqDEX2Mbkj2",  # NOQA
            "POST_URL": "https://fcm.googleapis.com/fcm/send",  # (optional)
            "MAX_RECIPIENTS": 1000,
        }
    },
}
