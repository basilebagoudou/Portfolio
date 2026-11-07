"""Journal des visites : un middleware qui enregistre chaque page vue.

D'où vient le visiteur :
- géographie : en-têtes ajoutés par Vercel (x-vercel-ip-country, -region, -city),
  donc aucun service externe n'est appelé ;
- provenance : en-tête Referer (Google, LinkedIn, GitHub…) ou paramètre utm_source.

Aucune adresse IP n'est enregistrée : seule une empreinte (hachage de l'IP, du
navigateur et de la date, salé avec SECRET_KEY) permet de compter les
visiteurs uniques d'une journée. Les robots, les visites de l'admin (toi,
connecté), tes propres navigateurs (cookie « bb_ne_pas_compter », posé via le
lien affiché dans le back-office) et les navigateurs qui envoient « Do Not
Track » / « Global Privacy Control » sont ignorés. Les visites de plus de
13 mois sont supprimées automatiquement.
"""
import logging
import random
import re
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

from .securite import empreinte, geo

logger = logging.getLogger(__name__)

ROBOTS = re.compile(
    r"bot|crawl|spider|slurp|preview|facebookexternalhit|embedly|curl|wget|python-|"
    r"httpclient|headless|lighthouse|monitor|scrapy|go-http|java/|okhttp|vercel",
    re.I,
)
CHEMINS_IGNORES = ("/admin", "/static", "/contact", "/favicon", "/robots.txt")

SOURCES_CONNUES = {
    "google": "Google", "bing": "Bing", "duckduckgo": "DuckDuckGo", "yahoo": "Yahoo",
    "linkedin": "LinkedIn", "lnkd.in": "LinkedIn", "github": "GitHub",
    "facebook": "Facebook", "instagram": "Instagram", "t.co": "X (Twitter)",
    "twitter": "X (Twitter)", "x.com": "X (Twitter)", "whatsapp": "WhatsApp",
    "wa.me": "WhatsApp", "telegram": "Telegram", "t.me": "Telegram",
    "notion": "Notion", "slack": "Slack", "discord": "Discord", "vercel.com": "Vercel",
    "mail.google": "Gmail", "outlook": "Outlook", "chatgpt": "ChatGPT", "claude.ai": "Claude",
}


def _source(request):
    utm = request.GET.get("utm_source", "").strip()
    if utm:
        return utm[:60], ""
    referent = request.META.get("HTTP_REFERER", "")[:500]
    hote = (urlparse(referent).hostname or "").lower().removeprefix("www.")
    if not hote:
        return "Accès direct", ""
    if hote == request.get_host().split(":")[0].lower():
        return "Navigation interne", referent
    for cle, nom in SOURCES_CONNUES.items():
        if cle in hote:
            return nom, referent
    return hote, referent


def _appareil(ua):
    if re.search(r"ipad|tablet", ua, re.I):
        return "Tablette"
    if re.search(r"mobi|iphone|android", ua, re.I):
        return "Mobile"
    return "Ordinateur"


def _navigateur(ua):
    for motif, nom in ((r"edg/", "Edge"), (r"opr/|opera", "Opera"), (r"samsungbrowser", "Samsung Internet"),
                       (r"firefox|fxios", "Firefox"), (r"chrome|crios", "Chrome"), (r"safari", "Safari")):
        if re.search(motif, ua, re.I):
            return nom
    return "Autre"


def _systeme(ua):
    for motif, nom in ((r"android", "Android"), (r"iphone|ipad|ios", "iOS"), (r"windows", "Windows"),
                       (r"mac os", "macOS"), (r"cros", "ChromeOS"), (r"linux", "Linux")):
        if re.search(motif, ua, re.I):
            return nom
    return "Autre"


COOKIE_IGNORER = "bb_ne_pas_compter"
CONSERVATION = timedelta(days=395)


def _a_enregistrer(request, response):
    if request.method != "GET" or response.status_code != 200:
        return False
    if not response.get("Content-Type", "").startswith("text/html"):
        return False
    if request.path.startswith(CHEMINS_IGNORES):
        return False
    if request.COOKIES.get(COOKIE_IGNORER):
        return False
    if request.META.get("HTTP_DNT") == "1" or request.META.get("HTTP_SEC_GPC") == "1":
        return False
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return False
    ua = request.META.get("HTTP_USER_AGENT", "")
    return bool(ua) and not ROBOTS.search(ua)


class VisiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.JOURNAL_VISITES and _a_enregistrer(request, response):
            try:
                self.enregistrer(request)
            except Exception:  # le journal ne doit jamais casser la page
                logger.exception("Journal des visites : échec de l'enregistrement")
        return response

    @staticmethod
    def enregistrer(request):
        from .models import Visite

        ua = request.META.get("HTTP_USER_AGENT", "")
        source, referent = _source(request)
        Visite.objects.create(
            chemin=request.path[:300],
            source=source,
            referent=referent,
            **geo(request),
            appareil=_appareil(ua),
            navigateur=_navigateur(ua),
            systeme=_systeme(ua),
            langue=request.META.get("HTTP_ACCEPT_LANGUAGE", "").split(",")[0][:20],
            visiteur=empreinte(request),
        )
        # Purge des vieilles visites, de temps en temps (≈ 1 page vue sur 200).
        if random.random() < 0.005:
            Visite.objects.filter(date__lt=timezone.now() - CONSERVATION).delete()
