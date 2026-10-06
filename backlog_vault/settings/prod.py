import os

from .base import *  # noqa: F403
from .base import BASE_DIR, MIDDLEWARE


def env_list(name, default=""):
    """Comma separated environment variable as a list."""
    return [item for item in os.environ.get(name, default).split(",") if item]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Required in production: there is no insecure fallback.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# e.g. DJANGO_ALLOWED_HOSTS=backlog-vault.onrender.com
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")

# Origins allowed to submit forms over HTTPS (with the scheme), e.g.
# DJANGO_CSRF_TRUSTED_ORIGINS=https://backlog-vault.onrender.com
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Demo login buttons are off unless DJANGO_DEMO_MODE=1 is set explicitly
# (for example on a public demo server with throw-away data).
DEMO_MODE = os.environ.get("DJANGO_DEMO_MODE", "0") == "1"

# HTTPS: the hosting proxy terminates TLS and sends X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Set DJANGO_SECURE_COOKIES=0 only to try the prod settings locally over http.
SECURE_COOKIES = os.environ.get("DJANGO_SECURE_COOKIES", "1") == "1"
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES

# Static files are served by WhiteNoise after `manage.py collectstatic`.
MIDDLEWARE = [
    MIDDLEWARE[0],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Email: SMTP when EMAIL_HOST is set, otherwise activation links are printed
# to the server log (the console backend).
if os.environ.get("EMAIL_HOST"):
    MAILERS = {
        "default": {
            "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "OPTIONS": {
                "host": os.environ["EMAIL_HOST"],
                "port": int(os.environ.get("EMAIL_PORT", "587")),
                "username": os.environ.get("EMAIL_HOST_USER", ""),
                "password": os.environ.get("EMAIL_HOST_PASSWORD", ""),
                "use_tls": os.environ.get("EMAIL_USE_TLS", "1") == "1",
            },
        },
    }
    DEFAULT_FROM_EMAIL = os.environ.get(
        "DEFAULT_FROM_EMAIL",
        os.environ.get("EMAIL_HOST_USER", "webmaster@localhost"),
    )
else:
    SILENCED_SYSTEM_CHECKS = ["mail.E001"]

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
