import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

DEBUG = os.environ.get("DEBUG")
DEBUG = DEBUG in ("True", "true", "1")  # noqa: WPS510

# Included components
include(
    "components/database.py",
    "components/password_validator.py",
    "components/internationalization.py",
    "components/application.py",
)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

# DDT repair from official doc (doesn't work)
if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "https://127.0.0.1:8080",
]


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logger
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
        },
    },
    "handlers": {
        "debug-console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["require_debug_true"],
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["debug-console"],
            "propagate": False,
        }
    },
}
