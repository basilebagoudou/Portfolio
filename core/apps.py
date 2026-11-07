from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class CoreConfig(AppConfig):
    name = "core"
    verbose_name = "Portfolio"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import securite  # noqa: F401  (branche les signaux de connexion)


class BackOfficeAdminConfig(AdminConfig):
    """L'admin Django, avec notre site (connexion protégée contre la force brute)."""
    default_site = "core.admin_site.BackOffice"
