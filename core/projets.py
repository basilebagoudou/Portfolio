"""Liste des projets du portfolio et de leurs ancres (#data-1, #ing-2…).

Partagée entre la page d'accueil (ancres des cartes) et le back-office
(choix du « projet lié » d'un article).
"""
from . import content


def nom_court(projet):
    """« Home Credit — prédiction… » -> « Home Credit »."""
    return {langue: texte.split(" — ")[0] for langue, texte in projet["titre"].items()}


def avec_ancres():
    """[(ancre, projet), …] dans l'ordre d'affichage."""
    paires = []
    for prefixe, projets in (("data", content.PROJETS_DATA), ("ing", content.PROJETS_ING)):
        for i, p in enumerate(projets):
            paires.append((f"{prefixe}-{i + 1}", p))
    return paires


def choix():
    """Choix pour le champ « projet » d'un article (admin)."""
    return [("", "— aucun —")] + [(ancre, nom_court(p)["fr"]) for ancre, p in avec_ancres()]


def nom(ancre):
    for a, p in avec_ancres():
        if a == ancre:
            return nom_court(p)
    return None
