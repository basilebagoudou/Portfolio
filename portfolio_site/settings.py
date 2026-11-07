"""Réglages Django du portfolio.

Le site n'a pas de base de données : tout le contenu vit dans core/content.py.
En production (Vercel), DEBUG est désactivé et les fichiers statiques sont
servis par WhiteNoise directement depuis les dossiers static/ des applis.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-uniquement-ne-pas-utiliser-en-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "0" if os.environ.get("VERCEL") else "1") == "1"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".vercel.app"]
ALLOWED_HOSTS += [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "portfolio_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
    },
]

WSGI_APPLICATION = "portfolio_site.wsgi.application"

DATABASES = {}

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = False
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Sur Vercel il n'y a pas d'étape collectstatic : WhiteNoise lit les fichiers
# directement dans core/static/ grâce aux finders.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
