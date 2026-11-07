"""Modèles du back-office : articles (écrits dans l'admin Django) et visites."""
import math
from datetime import date

import markdown
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import projets

FAMILLES = [
    ("data", "Data & machine learning"),
    ("bd", "Bases de données"),
    ("ing", "Ingénierie & déploiement"),
]

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]
MOIS_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December"]
MOTS_PAR_MINUTE = 200


class Sujet(models.Model):
    nom_fr = models.CharField("nom (FR)", max_length=60)
    nom_en = models.CharField("nom (EN)", max_length=60, blank=True,
                              help_text="Laisser vide pour reprendre le nom français.")
    famille = models.CharField(max_length=10, choices=FAMILLES, default="data",
                               help_text="Donne la couleur de l'étiquette.")

    class Meta:
        ordering = ["famille", "nom_fr"]

    def __str__(self):
        return self.nom_fr


def _markdown(texte):
    return mark_safe(markdown.markdown(texte, extensions=["fenced_code", "tables", "sane_lists"]))


def _minutes(texte):
    return max(1, math.ceil(len(texte.split()) / MOTS_PAR_MINUTE))


AIDE_MARKDOWN = (
    "Écrit en Markdown : ## Titre de partie · **gras** · *italique* · `code` · "
    "[lien](https://…) · listes avec « - » ou « 1. » · bloc de code entre deux lignes ```python et ```."
)


class Article(models.Model):
    titre_fr = models.CharField("titre (FR)", max_length=200)
    titre_en = models.CharField("titre (EN)", max_length=200, blank=True)
    slug = models.SlugField("adresse", max_length=120, unique=True,
                            help_text="Fin de l’URL : /articles/«&nbsp;adresse&nbsp;»/ (rempli automatiquement depuis le titre).")
    date_publication = models.DateField("date", default=date.today)
    publie = models.BooleanField("publié", default=False,
                                 help_text="Décoché = brouillon, visible seulement par toi (connecté).")
    resume_fr = models.TextField("résumé (FR)", help_text="2 à 3 phrases, affichées sur la carte et sous le titre.")
    resume_en = models.TextField("résumé (EN)", blank=True)
    corps_fr = models.TextField("texte (FR)", help_text=AIDE_MARKDOWN)
    corps_en = models.TextField("texte (EN)", blank=True,
                                help_text="Facultatif : si vide, la version anglaise affiche le texte français.")
    sujets = models.ManyToManyField(Sujet, blank=True)
    projet = models.CharField("projet lié", max_length=20, blank=True, choices=projets.choix,
                              help_text="Affiché dans la colonne de droite de l'article.")
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_publication", "-cree_le"]

    def __str__(self):
        return self.titre_fr

    def get_absolute_url(self):
        return reverse("article", args=[self.slug])

    # --- Données pour les gabarits (mêmes clés que les textes bilingues du site) ---
    def _bilingue(self, champ):
        fr = getattr(self, f"{champ}_fr")
        return {"fr": fr, "en": getattr(self, f"{champ}_en") or fr}

    def pour_gabarit(self, avec_corps=False):
        d = self.date_publication
        corps = self._bilingue("corps")
        donnees = {
            "slug": self.slug,
            "publie": self.publie,
            "titre": self._bilingue("titre"),
            "resume": self._bilingue("resume"),
            "date_txt": {"fr": f"{d.day} {MOIS_FR[d.month - 1]} {d.year}",
                         "en": f"{MOIS_EN[d.month - 1]} {d.day}, {d.year}"},
            "lecture": {"fr": f"{_minutes(corps['fr'])} min de lecture",
                        "en": f"{_minutes(corps['en'])} min read"},
            "sujets": [{"label": {"fr": s.nom_fr, "en": s.nom_en or s.nom_fr}, "famille": s.famille}
                       for s in self.sujets.all()],
            "projet": {"ancre": self.projet, "titre": projets.nom(self.projet)} if self.projet else None,
        }
        if avec_corps:
            donnees["corps"] = {langue: _markdown(texte) for langue, texte in corps.items()}
        return donnees


class Visite(models.Model):
    """Une page vue. Pas d'adresse IP stockée : seulement une empreinte du jour."""
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    chemin = models.CharField("page", max_length=300)
    source = models.CharField(max_length=200, db_index=True,
                              help_text="Site d'où vient le visiteur (ou « Accès direct »).")
    referent = models.URLField("lien d'origine", max_length=500, blank=True)
    pays = models.CharField(max_length=2, blank=True, db_index=True)
    region = models.CharField("région", max_length=80, blank=True)
    ville = models.CharField(max_length=120, blank=True)
    appareil = models.CharField(max_length=20, blank=True)
    navigateur = models.CharField(max_length=40, blank=True)
    systeme = models.CharField("système", max_length=40, blank=True)
    langue = models.CharField(max_length=20, blank=True)
    visiteur = models.CharField("empreinte du jour", max_length=16, db_index=True,
                                help_text="Identique pour un même visiteur le même jour (sans stocker son IP).")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date:%d/%m/%Y %H:%M} · {self.chemin}"


class Message(models.Model):
    """Message envoyé par le formulaire de contact (gardé même si l'email échoue)."""
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    langue = models.CharField(max_length=2, default="fr")
    pays = models.CharField(max_length=2, blank=True)
    ville = models.CharField(max_length=120, blank=True)
    expediteur = models.CharField("empreinte", max_length=16, db_index=True,
                                  help_text="Sert à limiter le nombre d'envois (sans stocker l'IP).")
    email_envoye = models.BooleanField("notification email envoyée", default=False)
    lu = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.nom} <{self.email}> · {self.date:%d/%m/%Y %H:%M}"


class Connexion(models.Model):
    """Journal des connexions au back-office (sécurité)."""
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    identifiant = models.CharField(max_length=150, blank=True)
    reussie = models.BooleanField("réussie", default=False)
    ip = models.GenericIPAddressField(null=True, blank=True)
    pays = models.CharField(max_length=2, blank=True)
    ville = models.CharField(max_length=120, blank=True)
    navigateur = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "connexion au back-office"
        verbose_name_plural = "connexions au back-office"

    def __str__(self):
        return f"{'✓' if self.reussie else '✗'} {self.identifiant} · {self.date:%d/%m/%Y %H:%M}"
