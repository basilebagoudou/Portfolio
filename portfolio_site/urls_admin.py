"""URL du back-office (SITE_ROLE=admin), servi sur une autre adresse que le portfolio.

- /           : l'admin Django (articles, messages, visites, connexions)
- /apercu/…   : le portfolio tel qu'il sera publié, brouillons compris,
                réservé aux comptes connectés.
"""
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include, path

from .urls import routes_site

urlpatterns = [
    path("apercu/", include(routes_site(proteger=staff_member_required))),
    path("", admin.site.urls),
]

handler404 = "core.views.page_introuvable"
