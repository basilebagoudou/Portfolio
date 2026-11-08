"""Logo du site : une mini-matrice compétences × projets (comme la grande, en
page d'accueil), suivie du nom. Chaque point allumé = une techno utilisée dans
un projet, coloré selon sa famille (data, bases de données, ingénierie)."""
from . import content

LIGNES = 5  # les 5 technos les plus utilisées


def marque(request):
    from .views import _famille_de, _matrice_competences  # import tardif (évite la boucle)

    projets = content.PROJETS_DATA + content.PROJETS_ING
    matrice = _matrice_competences(projets)
    lignes = matrice["lignes"]  # déjà triées de la plus utilisée à la moins utilisée
    # La techno la plus utilisée de chaque famille, puis les suivantes par usage.
    choisies = []
    for famille in ("data", "bd", "ing"):
        tete = next((l for l in lignes if _famille_de(l["tech"]) == famille), None)
        if tete:
            choisies.append(tete)
    choisies += [l for l in lignes if l not in choisies][:LIGNES - len(choisies)]
    choisies.sort(key=lignes.index)
    points = []
    for ligne in choisies:
        famille = _famille_de(ligne["tech"])
        points += [famille if utilise else "" for utilise in ligne["cellules"]]
    return {"marque": {"points": points, "colonnes": len(projets)}}


def _version_statique():
    """Suffixe ?v= des CSS/JS : change à chaque déploiement (commit Vercel)
    ou à chaque modification des fichiers en local, pour contourner le cache."""
    import os
    from pathlib import Path

    sha = os.environ.get("VERCEL_GIT_COMMIT_SHA", "")[:8]
    if sha:
        return sha
    dossier = Path(__file__).resolve().parent / "static" / "core"
    return str(int(max(f.stat().st_mtime for f in dossier.rglob("*.*") if f.suffix in (".css", ".js"))))


def version(request):
    return {"version_statique": _version_statique()}
