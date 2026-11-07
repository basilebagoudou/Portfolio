from collections import Counter
from datetime import date

import logging

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

from . import content, securite
from .content import t
from .forms import ContactForm, jeton_horodatage
from .models import Article, Message
from .projets import nom_court as _nom_court
from .visites import COOKIE_IGNORER

logger = logging.getLogger(__name__)
STATUTS_CONTACT = {"ok", "erreur", "invalide", "limite"}


def _matrice_competences(projets):
    """Matrice compétences × projets, calculée à partir des technos de chaque projet.

    Les lignes sont triées de la compétence la plus utilisée à la moins utilisée.
    """
    usage = Counter(tech for p in projets for tech in p["tech"])
    lignes = []
    for tech, nb in sorted(usage.items(), key=lambda kv: (-kv[1], kv[0].lower())):
        lignes.append({
            "tech": tech,
            "nb": nb,
            "cellules": [tech in p["tech"] for p in projets],
        })
    return {"colonnes": [_nom_court(p) for p in projets], "lignes": lignes}


# Familles de compétences (dans l'ordre de COMPETENCES) : clé CSS + couleur.
FAMILLES = ["data", "bd", "ing"]


def _famille_de(tech):
    """Famille d'une techno d'après les groupes de COMPETENCES (ingénierie par défaut)."""
    for cle, categorie in zip(FAMILLES, content.COMPETENCES):
        if tech in [i for i in categorie["items"] if isinstance(i, str)]:
            return cle
    return "ing"


def _enrichir(projets, prefixe):
    """Ajoute à chaque projet : ancre, signature de couleurs et blocs du graphique.

    La signature est la répartition de sa stack par famille de compétences
    (bande colorée en tête de carte) ; les blocs servent au graphique
    « vue d'ensemble » (un bloc par techno, empilés par famille).
    """
    enrichis = []
    for i, p in enumerate(projets):
        familles = [_famille_de(tech) for tech in p["tech"]]
        total = len(familles)
        signature = [{"famille": f, "pct": round(100 * familles.count(f) / total, 2)}
                     for f in FAMILLES if f in familles]
        blocs = sorted(zip(p["tech"], familles), key=lambda tf: FAMILLES.index(tf[1]))
        enrichis.append(dict(
            p,
            ancre=f"{prefixe}-{i + 1}",
            signature=signature,
            blocs=[{"tech": tech, "famille": f} for tech, f in blocs],
            court=_nom_court(p),
            data_tech="|".join(p["tech"]),
        ))
    return enrichis


def _couverture(projets):
    """Pour chaque famille de compétences : combien de projets l'utilisent."""
    lignes = []
    for cle, categorie in zip(FAMILLES, content.COMPETENCES):
        nb = sum(1 for p in projets if any(_famille_de(t) == cle for t in p["tech"]))
        lignes.append({"famille": cle, "nb": nb, "total": len(projets),
                       "pct": round(100 * nb / len(projets))})
    return lignes


def accueil(request):
    projets_data = _enrichir(content.PROJETS_DATA, "data")
    projets_ing = _enrichir(content.PROJETS_ING, "ing")
    projets = projets_data + projets_ing
    nb_modules = len(content.GCI_MODULES)
    chiffres = [
        {"valeur": 171202, "texte": "171 202", "texte_en": "171,202",
         "label": t("clients — jeu de données risque de crédit", "clients — credit risk dataset")},
        {"valeur": 100000, "texte": "100 000", "texte_en": "100,000",
         "label": t("abonnés — jeu de données télécom", "subscribers — telecom dataset")},
        {"valeur": nb_modules, "texte": str(nb_modules), "texte_en": str(nb_modules),
         "label": t("modules de data science — programme U. Tokyo",
                    "data science modules — U. Tokyo program")},
        {"valeur": len(projets), "texte": str(len(projets)), "texte_en": str(len(projets)),
         "label": t("projets, dont 2 en ligne", "projects, 2 live")},
    ]
    return render(request, "core/index.html", {
        "profil": content.PROFIL,
        "chiffres": chiffres,
        "apports": content.APPORTS,
        "pipeline": content.PIPELINE,
        "projets_data": projets_data,
        "projets_ing": projets_ing,
        "projets_tous": projets,
        "max_tech": max(len(p["tech"]) for p in projets),
        "matrice": _matrice_competences(projets),
        "parcours": content.PARCOURS,
        "gci_modules": content.GCI_MODULES,
        "competences": [dict(c, famille=f, couverture=cv) for c, f, cv in
                        zip(content.COMPETENCES, FAMILLES, _couverture(projets))],
        "annee": date.today().year,
        "ancre": "",
        "page": "accueil",
        "contact_ts": jeton_horodatage(),
        "contact_statut": request.GET.get("contact") if request.GET.get("contact") in STATUTS_CONTACT else "",
    })


def _notifier(message):
    """Envoie une copie du message par email ; renvoie True si c'est parti."""
    if not settings.EMAIL_CONFIGURE:
        return False
    email = EmailMessage(
        subject=f"[Portfolio] Message de {message.nom}",
        body=(f"Nom : {message.nom}\nEmail : {message.email}\nLangue : {message.langue}\n"
              f"Lieu : {message.ville or '?'} ({message.pays or '?'})\n\n{message.message}"),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[message.email],
    )
    try:
        email.send()
        return True
    except Exception:  # SMTP indisponible, identifiants refusés…
        logger.exception("Formulaire de contact : échec de la notification email")
        return False


def _traiter_contact(request, form):
    if not form.is_valid():
        return "invalide"
    if form.est_robot():
        return "ok"  # on ne dit pas au robot qu'il a été repéré
    if securite.trop_de_messages(request):
        return "limite"
    d = form.cleaned_data
    g = securite.geo(request)
    try:
        message = Message.objects.create(
            nom=d["nom"], email=d["email"], message=d["message"], langue=d.get("langue") or "fr",
            pays=g["pays"], ville=g["ville"], expediteur=securite.empreinte(request),
        )
    except Exception:
        logger.exception("Formulaire de contact : enregistrement impossible")
        message = None
    envoye = _notifier(message) if message else False
    if message and envoye:
        Message.objects.filter(pk=message.pk).update(email_envoye=True)
    # Sur la base temporaire (pas encore de vraie base), seul l'email compte.
    garde = message is not None and settings.BASE_PERSISTANTE
    return "ok" if (garde or envoye) else "erreur"


@require_POST
def contact(request):
    """Reçoit le formulaire. Répond en JSON (envoi en JS) ou redirige (sans JS)."""
    form = ContactForm(request.POST)
    statut = _traiter_contact(request, form)
    if "application/json" in request.headers.get("Accept", ""):
        codes = {"ok": 200, "invalide": 400, "limite": 429, "erreur": 502}
        return JsonResponse({"statut": statut, "champs": list(form.errors)}, status=codes[statut])
    return redirect(f"{reverse('accueil')}?contact={statut}#contact")


def _contexte_page(**extra):
    return {"annee": date.today().year, "ancre": reverse("accueil"), "page": "articles", **extra}


def _articles_visibles(request):
    qs = Article.objects.prefetch_related("sujets")
    # Les brouillons ne sont visibles que dans l'aperçu du back-office (connecté).
    return qs if request.user.is_staff else qs.filter(publie=True)


def articles(request):
    liste = [a.pour_gabarit() for a in _articles_visibles(request)]
    return render(request, "core/articles.html", _contexte_page(articles=liste))


def article(request, slug):
    objet = _articles_visibles(request).filter(slug=slug).first()
    if objet is None:
        raise Http404("Article introuvable")
    autres = [a.pour_gabarit() for a in _articles_visibles(request).exclude(pk=objet.pk)[:3]]
    return render(request, "core/article.html",
                  _contexte_page(article=objet.pour_gabarit(avec_corps=True), autres=autres))


def page_introuvable(request, exception=None):
    return render(request, "core/404.html", _contexte_page(page="404"), status=404)


def robots(request):
    lignes = ["User-agent: *", "Allow: /", "Disallow: /contact/", "",
              f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}"]
    return HttpResponse("\n".join(lignes) + "\n", content_type="text/plain")


@cache_page(3600)
def sitemap(request):
    adresses = [(reverse("accueil"), None), (reverse("articles"), None)]
    adresses += [(a.get_absolute_url(), a.modifie_le.date().isoformat())
                 for a in Article.objects.filter(publie=True)]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for chemin, modif in adresses:
        xml.append(f"  <url><loc>{request.build_absolute_uri(chemin)}</loc>"
                   + (f"<lastmod>{modif}</lastmod>" if modif else "") + "</url>")
    xml.append("</urlset>")
    return HttpResponse("\n".join(xml), content_type="application/xml")


def ne_pas_compter(request, jeton):
    """Lien affiché dans le back-office : pose un cookie pour exclure ce navigateur des stats."""
    try:
        signing.loads(jeton, salt="portfolio.visites")
    except signing.BadSignature:
        raise Http404()
    reponse = redirect("accueil")
    reponse.set_cookie(COOKIE_IGNORER, "1", max_age=2 * 365 * 24 * 3600, secure=not settings.DEBUG,
                       httponly=True, samesite="Lax")
    return reponse
