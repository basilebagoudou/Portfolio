from datetime import date

from django.shortcuts import render

from . import content


def accueil(request):
    return render(request, "core/index.html", {
        "parcours": content.PARCOURS,
        "competences": content.COMPETENCES,
        "projets": content.PROJETS,
        "gci_modules": content.GCI_MODULES,
        "annee": date.today().year,
    })
