# flake8: noqa: F405

from .base import *

INSTALLED_APPS += ["django_extensions"]

SECRET_KEY = "s@zed1d0-lxv#^!8+*8g+n*xyiy7_ajw-rk^z8zwlm%5d@qz8("

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_FILE_STORAGE = (
    "easysolar_api.core.storages.local_media_storage.LocalMediaStorage"
)

STATIC_ROOT = BASE_DIR / "static"

BROWSERLESS_API_ENDPOINT = "http://localhost:3000"

# DB logging
# LOGGING["loggers"]["django.db.backends"] = {
#     "handlers": ["sql_handler"],
#     "level": "DEBUG",
#     "propagate": False,
# }
# LOGGING["loggers"]["django.server"] = {
#     'handlers': ['django.server'],
#     'level': 'INFO',
#     'propagate': False,
# }
#
# LOGGING["formatters"]["sql_formatter"] = {
#     "()": "apps.core.sql_formatter.SqlFormatter",
#     "format": "%(levelname)s %(message)s",
# }
#
# LOGGING["handlers"]["sql_handler"] = {
#     "level": "DEBUG",
#     "class": "logging.FileHandler",
#     'filename': 'general.log',
#     "formatter": "sql_formatter",
# }
# LOGGING["handlers"]["django.server"] = {
#     "level": "DEBUG",
#     "class": "logging.FileHandler",
#     'filename': 'general.log',
#     "formatter": "sql_formatter",
# }

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
            "class": "logging.FileHandler",
            "filename": "general.log",
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
