from django.urls import path

from core import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
    path("contact/", views.contact, name="contact"),
    path("articles/", views.articles, name="articles"),
    path("articles/<slug:slug>/", views.article, name="article"),
]
