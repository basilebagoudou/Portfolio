from collections import Counter
from datetime import date

from django.shortcuts import render

from . import content
from .content import t


def _nom_court(projet):
    """« Home Credit — prédiction… » -> « Home Credit » (pour les colonnes de la matrice)."""
    return {langue: texte.split(" — ")[0] for langue, texte in projet["titre"].items()}


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


def accueil(request):
    projets = content.PROJETS_DATA + content.PROJETS_ING
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
        "projets_data": content.PROJETS_DATA,
        "projets_ing": content.PROJETS_ING,
        "matrice": _matrice_competences(projets),
        "parcours": content.PARCOURS,
        "gci_modules": content.GCI_MODULES,
        "competences": content.COMPETENCES,
        "annee": date.today().year,
    })
