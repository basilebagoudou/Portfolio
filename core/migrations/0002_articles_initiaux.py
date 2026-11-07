"""Données de départ : les sujets et les deux premiers articles.

Le texte des articles est lu dans core/articles_initiaux/*.md (uniquement à
cette migration). Ensuite, tout se modifie dans le back-office.
"""
from datetime import date
from pathlib import Path

from django.db import migrations

DOSSIER = Path(__file__).resolve().parent.parent / "articles_initiaux"

SUJETS = [
    ("Machine learning", "Machine learning", "data"),
    ("Évaluation de modèles", "Model evaluation", "data"),
    ("Données déséquilibrées", "Imbalanced data", "data"),
    ("Python", "Python", "data"),
    ("SQL", "SQL", "bd"),
    ("Django", "Django", "ing"),
    ("Déploiement", "Deployment", "ing"),
]

ARTICLES = [
    {
        "slug": "home-credit-accuracy-roc-auc",
        "titre_fr": "92 % d'accuracy sans rien apprendre : pourquoi Home Credit se juge à la ROC AUC",
        "titre_en": "92% accuracy while learning nothing: why Home Credit is judged on ROC AUC",
        "resume_fr": "Sur 171 202 clients, seuls 8,1 % font défaut. Un modèle qui ne prédit jamais le "
                     "défaut a donc l'air excellent. Ce que ça m'a appris sur le choix de la métrique, "
                     "avec le code.",
        "resume_en": "Out of 171,202 clients, only 8.1% default. A model that never predicts a default "
                     "therefore looks excellent. What this taught me about choosing a metric, with the code.",
        "sujets": ["Machine learning", "Évaluation de modèles", "Données déséquilibrées"],
        "projet": "data-1",
    },
    {
        "slug": "portfolio-django-sans-base-de-donnees",
        "titre_fr": "Un portfolio Django sans base de données, déployé sur Vercel",
        "titre_en": "A Django portfolio with no database, deployed on Vercel",
        "resume_fr": "Pourquoi j'ai migré mon site statique vers Django, comment le contenu bilingue vit "
                     "dans un simple fichier Python, et ce qu'il faut savoir pour faire tourner Django "
                     "sur Vercel.",
        "resume_en": "Why I moved my static site to Django, how the bilingual content lives in a plain "
                     "Python file, and what you need to know to run Django on Vercel.",
        "sujets": ["Django", "Déploiement", "Python"],
        "projet": "ing-3",
    },
]


def creer(apps, schema_editor):
    Sujet = apps.get_model("core", "Sujet")
    Article = apps.get_model("core", "Article")
    sujets = {fr: Sujet.objects.get_or_create(nom_fr=fr, defaults={"nom_en": en, "famille": fam})[0]
              for fr, en, fam in SUJETS}
    for a in ARTICLES:
        if Article.objects.filter(slug=a["slug"]).exists():
            continue
        article = Article.objects.create(
            slug=a["slug"], titre_fr=a["titre_fr"], titre_en=a["titre_en"],
            resume_fr=a["resume_fr"], resume_en=a["resume_en"],
            corps_fr=(DOSSIER / f"{a['slug']}.fr.md").read_text(encoding="utf-8"),
            corps_en=(DOSSIER / f"{a['slug']}.en.md").read_text(encoding="utf-8"),
            projet=a["projet"], publie=True, date_publication=date(2026, 11, 7),
        )
        article.sujets.set([sujets[s] for s in a["sujets"]])


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(creer, migrations.RunPython.noop)]
