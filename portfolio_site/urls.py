"""URL du site public (portfolio). Aucune page d'administration ici."""
from django.urls import path

from core import views
from core.flux import FluxArticles


def routes_site(proteger=None):
    """Routes du portfolio. `proteger` enveloppe chaque vue (aperçu réservé au back-office)."""
    p = proteger or (lambda vue: vue)
    return [
        path("", p(views.accueil), name="accueil"),
        path("contact/", p(views.contact), name="contact"),
        path("articles/", p(views.articles), name="articles"),
        path("articles/rss/", p(FluxArticles()), name="articles_rss"),
        path("articles/<slug:slug>/", p(views.article), name="article"),
    ]


urlpatterns = routes_site() + [
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("ne-pas-compter/<str:jeton>/", views.ne_pas_compter, name="ne_pas_compter"),
]

handler404 = "core.views.page_introuvable"
