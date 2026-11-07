"""Réglages Django du portfolio.

Un même code, deux sites séparés (variable d'environnement SITE_ROLE) :

- « public » (par défaut) : le portfolio. Aucune page d'administration.
- « admin » : le back-office (articles, messages, visites), sur une autre
  adresse en production et un autre port en local :
      python manage.py runserver 8000                  # portfolio
      SITE_ROLE=admin python manage.py runserver 8001  # back-office

Les deux partagent la même base de données (DATABASE_URL, Postgres en ligne).
"""
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
SUR_VERCEL = bool(os.environ.get("VERCEL"))

ROLE = os.environ.get("SITE_ROLE", "public")
if ROLE not in ("public", "admin"):
    raise ImproperlyConfigured("SITE_ROLE doit valoir « public » ou « admin ».")

DEBUG = os.environ.get("DJANGO_DEBUG", "0" if SUR_VERCEL else "1") == "1"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if SUR_VERCEL and ROLE == "admin":
        raise ImproperlyConfigured("DJANGO_SECRET_KEY est obligatoire pour le back-office.")
    SECRET_KEY = "dev-uniquement-ne-pas-utiliser-en-production"

# Adresse publique du portfolio (liens depuis le back-office).
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://basile-bagoudou.vercel.app" if SUR_VERCEL
                            else "http://127.0.0.1:8000").rstrip("/")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".vercel.app"]
ALLOWED_HOSTS += [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]

INSTALLED_APPS = [
    "core.apps.CoreConfig",  # en premier : ses gabarits admin/ priment sur ceux de Django
    "core.apps.BackOfficeAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.securite.EnTetesSecuriteMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.visites.VisiteMiddleware",
]

ROOT_URLCONF = "portfolio_site.urls_admin" if ROLE == "admin" else "portfolio_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

WSGI_APPLICATION = "portfolio_site.wsgi.application"

# ===== Base de données =====
# En ligne : Postgres (Neon, via l'onglet Storage de Vercel), qui fournit
# DATABASE_URL (ou POSTGRES_URL). Sans base configurée, le site public tourne
# sur une base SQLite temporaire (/tmp, effacée à chaque redémarrage) qui
# contient les articles de départ : le site reste en ligne en attendant.
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or ""
BASE_PERSISTANTE = bool(DATABASE_URL) or not SUR_VERCEL
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=0, conn_health_checks=True)}
elif SUR_VERCEL:
    if ROLE == "admin":
        raise ImproperlyConfigured("Le back-office a besoin d'une vraie base : définir DATABASE_URL.")
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "/tmp/portfolio.sqlite3"}}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Journal des visites : seulement sur le site public, et seulement si la base
# est persistante (inutile de remplir une base temporaire).
JOURNAL_VISITES = ROLE == "public" and BASE_PERSISTANTE

LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Sur Vercel il n'y a pas d'étape collectstatic : WhiteNoise lit les fichiers
# directement dans les dossiers static/ des applis grâce aux finders.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# ===== Comptes et mots de passe =====
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ===== Sécurité HTTP =====
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict" if ROLE == "admin" else "Lax"
CSRF_COOKIE_SAMESITE = "Strict" if ROLE == "admin" else "Lax"
SESSION_COOKIE_AGE = 8 * 3600            # session du back-office : 8 h maximum
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o]
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024  # 1 Mo par requête : largement assez pour un article

# ===== Formulaire de contact =====
# Les messages sont toujours enregistrés dans le back-office. En plus, si
# EMAIL_HOST_PASSWORD est défini (mot de passe d'application Gmail), une
# notification part par email vers CONTACT_EMAIL.
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
    # En local : les emails s'affichent dans le terminal au lieu de partir.
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    EMAIL_CONFIGURE = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"core": {"handlers": ["console"], "level": "INFO"}},
}
