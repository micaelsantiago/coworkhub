from django.core.exceptions import ImproperlyConfigured

from config.settings.base import *  # noqa: F403

if SECRET_KEY == "unsafe-development-key":  # noqa: F405
    raise ImproperlyConfigured("DJANGO_SECRET_KEY deve ser configurada em produção.")

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
