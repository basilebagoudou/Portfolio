"""Chargement des articles : métadonnées dans content.ARTICLES, texte en Markdown.

Chaque article a deux fichiers, core/articles/<slug>.fr.md et <slug>.en.md.
Le Markdown est converti en HTML une seule fois par processus (lru_cache).
"""
import math
from datetime import date
from functools import lru_cache
from pathlib import Path

import markdown
from django.utils.safestring import mark_safe

from . import content

DOSSIER = Path(__file__).resolve().parent / "articles"
MOTS_PAR_MINUTE = 200

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
MOIS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"]


def _date(iso):
    d = date.fromisoformat(iso)
    return {"fr": f"{d.day} {MOIS_FR[d.month - 1]} {d.year}",
            "en": f"{MOIS_EN[d.month - 1]} {d.day}, {d.year}"}


def _lecture(texte):
    minutes = max(1, math.ceil(len(texte.split()) / MOTS_PAR_MINUTE))
    return {"fr": f"{minutes} min de lecture", "en": f"{minutes} min read"}


@lru_cache(maxsize=None)
def _article(slug):
    meta = next((a for a in content.ARTICLES if a["slug"] == slug), None)
    if meta is None:
        return None
    textes = {langue: (DOSSIER / f"{slug}.{langue}.md").read_text(encoding="utf-8")
              for langue in ("fr", "en")}
    corps = {langue: mark_safe(markdown.markdown(
                 texte, extensions=["fenced_code", "tables", "sane_lists"]))
             for langue, texte in textes.items()}
    lecture = {"fr": _lecture(textes["fr"])["fr"], "en": _lecture(textes["en"])["en"]}
    return dict(meta, date_txt=_date(meta["date"]), lecture=lecture, corps=corps)


def tous():
    """Tous les articles, du plus récent au plus ancien."""
    articles = [_article(a["slug"]) for a in content.ARTICLES]
    return sorted(articles, key=lambda a: a["date"], reverse=True)


def un(slug):
    return _article(slug)
