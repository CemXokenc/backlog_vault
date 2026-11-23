from .base import *  # noqa: F403
from .base import BASE_DIR

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Header buttons that sign in as the demo admin, moderator or user.
DEMO_MODE = True

# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
