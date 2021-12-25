# flake8: noqa: F405

from .base import *

INSTALLED_APPS += ["django_extensions"]

SECRET_KEY = "django-insecure-cs$x8+4o#wdf91@se-&^id&lmw$af+phju&i=)%@c^r+ay@q9*"

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_FILE_STORAGE = (
    "easysolar_api.core.storages.local_media_storage.LocalMediaStorage"
)

STATIC_ROOT = BASE_DIR / "static"

BROWSERLESS_API_ENDPOINT = "http://localhost:3000"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        "sql_formatter": {
            "()": "apps.core.sql_formatter.SqlFormatter",
            "format": "%(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "sql_handler": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "sql_formatter",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["sql_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
