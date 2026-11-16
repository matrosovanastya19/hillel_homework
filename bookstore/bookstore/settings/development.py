from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "web"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "bookstore_db",
        "USER": "postgres",
        "PASSWORD": "postgrespassword",
        "HOST": "db",
        "PORT": "5432",
    }
}
