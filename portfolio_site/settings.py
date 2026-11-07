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
    "django.middleware.csrf.CsrfViewMiddleware",
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

# ===== Formulaire de contact =====
# Les messages partent par SMTP (Gmail par défaut). À définir sur Vercel :
#   EMAIL_HOST_USER     adresse Gmail qui envoie
#   EMAIL_HOST_PASSWORD mot de passe d'application Google (pas le mot de passe du compte)
#   CONTACT_EMAIL       (facultatif) adresse qui reçoit les messages
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or "webmaster@localhost"
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "basile2bagoudou@gmail.com")
EMAIL_CONFIGURE = bool(EMAIL_HOST_PASSWORD)
if DEBUG and not EMAIL_CONFIGURE:
    # En local : les messages s'affichent dans le terminal au lieu de partir.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_CONFIGURE = True

LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"core": {"handlers": ["console"], "level": "INFO"}},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
