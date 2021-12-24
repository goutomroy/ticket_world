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

LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["django.db"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}