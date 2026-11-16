from .base import *
import os
import dj_database_url

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# Підключення до БД через URL (стандарт для хмарних сервісів)
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1"),
    }
}

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Налаштування WhiteNoise для стиснення та кешування статики
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'