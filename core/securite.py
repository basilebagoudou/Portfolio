"""Mesures de sécurité : en-têtes HTTP, anti-force brute du back-office, limites."""
import hashlib
from datetime import date, timedelta
from urllib.parse import unquote

from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils import timezone

# ===== Identification du client (sans stocker l'IP en clair hors journal de sécurité) =====
def ip_client(request):
    transmis = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return transmis.split(",")[0].strip() if transmis else request.META.get("REMOTE_ADDR", "")


def empreinte(request):
    """Hachage salé (IP + navigateur + jour) : compte sans conserver l'adresse IP."""
    ua = request.META.get("HTTP_USER_AGENT", "")
    brut = f"{settings.SECRET_KEY}|{date.today().isoformat()}|{ip_client(request)}|{ua}"
    return hashlib.sha256(brut.encode()).hexdigest()[:16]


def geo(request):
    """Pays / région / ville fournis par Vercel (vides en local)."""
    m = request.META
    return {
        "pays": m.get("HTTP_X_VERCEL_IP_COUNTRY", "")[:2].upper(),
        "region": unquote(m.get("HTTP_X_VERCEL_IP_COUNTRY_REGION", ""))[:80],
        "ville": unquote(m.get("HTTP_X_VERCEL_IP_CITY", ""))[:120],
    }


# ===== En-têtes de sécurité =====
CSP_PUBLIC = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' https://fonts.googleapis.com",
    "style-src-attr 'unsafe-inline'",  # variables CSS (style="--w: 40%") des graphiques
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data:",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
])
CSP_ADMIN = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data:",
    "connect-src 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "object-src 'none'",
])


class EnTetesSecuriteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.csp = CSP_ADMIN if settings.ROLE == "admin" else CSP_PUBLIC

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Content-Security-Policy", self.csp)
        response.setdefault("Permissions-Policy",
                            "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()")
        response.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        if settings.ROLE == "admin":
            # Le back-office ne doit jamais apparaître dans un moteur de recherche
            # ni rester en cache.
            response["X-Robots-Tag"] = "noindex, nofollow"
            response.setdefault("Cache-Control", "no-store")
        return response


# ===== Anti-force brute sur la page de connexion =====
FENETRE = timedelta(minutes=15)
MAX_ECHECS_IP = 5        # par adresse IP sur 15 min
MAX_ECHECS_TOTAL = 30    # toutes IP confondues sur 15 min (attaque distribuée)


def connexion_bloquee(request):
    from .models import Connexion

    depuis = timezone.now() - FENETRE
    echecs = Connexion.objects.filter(reussie=False, date__gte=depuis)
    return (echecs.filter(ip=ip_client(request) or None).count() >= MAX_ECHECS_IP
            or echecs.count() >= MAX_ECHECS_TOTAL)


def _journaliser(request, identifiant, reussie):
    from .models import Connexion

    if request is None:
        return
    g = geo(request)
    Connexion.objects.create(
        identifiant=(identifiant or "")[:150], reussie=reussie, ip=ip_client(request) or None,
        pays=g["pays"], ville=g["ville"], navigateur=request.META.get("HTTP_USER_AGENT", "")[:300],
    )


@receiver(user_login_failed)
def _echec(sender, credentials, request=None, **kwargs):
    _journaliser(request, credentials.get("username"), False)


@receiver(user_logged_in)
def _succes(sender, request, user, **kwargs):
    _journaliser(request, user.get_username(), True)


# ===== Limite du formulaire de contact =====
MAX_MESSAGES_HEURE = 5


def trop_de_messages(request):
    from .models import Message

    return Message.objects.filter(expediteur=empreinte(request),
                                  date__gte=timezone.now() - timedelta(hours=1)).count() >= MAX_MESSAGES_HEURE
