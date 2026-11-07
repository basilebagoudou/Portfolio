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
    })
