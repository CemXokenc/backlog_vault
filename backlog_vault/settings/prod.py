import os

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Required in production: there is no insecure fallback.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# Comma separated list, e.g. DJANGO_ALLOWED_HOSTS=example.com,www.example.com
ALLOWED_HOSTS = [
    host
    for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host
]

# Demo login buttons are off unless DJANGO_DEMO_MODE=1 is set explicitly
# (for example on a public demo server with throw-away data).
DEMO_MODE = os.environ.get("DJANGO_DEMO_MODE", "0") == "1"

# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": int(os.environ["POSTGRES_DB_PORT"]),
        "OPTIONS": {"sslmode": "require"},
        # Required behind a transaction pooler (e.g. Neon's -pooler host).
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}
