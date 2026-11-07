import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio_site.settings")

application = get_wsgi_application()


def _preparer_base():
    """Au démarrage d'une instance Vercel : migrations, puis compte du back-office.

    - `migrate` ne fait rien si la base est déjà à jour (quelques requêtes).
    - Le compte admin est créé une seule fois à partir de DJANGO_SUPERUSER_USERNAME,
      DJANGO_SUPERUSER_PASSWORD (et DJANGO_SUPERUSER_EMAIL), à définir uniquement
      sur le projet Vercel du back-office. Il n'est jamais écrasé ensuite : si tu
      changes ton mot de passe dans le back-office, c'est lui qui compte.
    """
    from django.conf import settings
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=0)
    nom = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    mdp = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    if settings.ROLE == "admin" and nom and mdp:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not User.objects.filter(username=nom).exists():
            User.objects.create_superuser(nom, os.environ.get("DJANGO_SUPERUSER_EMAIL", ""), mdp)


if os.environ.get("VERCEL"):
    try:
        _preparer_base()
    except Exception:
        logging.getLogger("core").exception("Préparation de la base impossible")

# Vercel cherche une variable nommée « app » dans le point d'entrée.
app = application
