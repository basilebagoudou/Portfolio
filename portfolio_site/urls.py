from django.urls import path

from core import views

urlpatterns = [
    path("", views.accueil, name="accueil"),
]
