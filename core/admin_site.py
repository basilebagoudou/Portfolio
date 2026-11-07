from django.contrib import admin
from django.template.response import TemplateResponse

from . import securite


class BackOffice(admin.AdminSite):
    site_header = "Back-office · Basile Bagoudou"
    site_title = "Back-office portfolio"
    index_title = "Articles, messages et visites"
    site_url = "/apercu/"

    def login(self, request, extra_context=None):
        # Trop d'échecs récents : on refuse avant même de vérifier le mot de passe.
        if request.method == "POST" and securite.connexion_bloquee(request):
            return TemplateResponse(request, "admin/connexion_bloquee.html",
                                    {**self.each_context(request), "title": "Connexion bloquée"},
                                    status=429)
        return super().login(request, extra_context)
