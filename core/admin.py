"""Back-office (admin Django) : écrire les articles et consulter les visites."""
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core import signing
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.html import format_html

from .models import Article, Connexion, Message, Sujet, Visite


def drapeau(code):
    """« TG » -> 🇹🇬 (indicateurs régionaux Unicode)."""
    if len(code) != 2 or not code.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


# ===== ARTICLES =====
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "resume_fr": forms.Textarea(attrs={"rows": 3, "cols": 90}),
            "resume_en": forms.Textarea(attrs={"rows": 3, "cols": 90}),
            "corps_fr": forms.Textarea(attrs={"rows": 28, "cols": 90, "class": "md-editor"}),
            "corps_en": forms.Textarea(attrs={"rows": 28, "cols": 90, "class": "md-editor"}),
        }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    list_display = ("titre_fr", "date_publication", "publie", "lecture", "voir")
    list_display_links = ("titre_fr",)
    list_editable = ("publie",)
    list_filter = ("publie", "sujets")
    search_fields = ("titre_fr", "titre_en", "corps_fr")
    prepopulated_fields = {"slug": ("titre_fr",)}
    filter_horizontal = ("sujets",)
    date_hierarchy = "date_publication"
    actions = ["publier", "depublier"]
    fieldsets = (
        ("Publication", {"fields": ("titre_fr", "slug", "date_publication", "publie", "sujets", "projet")}),
        ("Français", {"fields": ("resume_fr", "corps_fr")}),
        ("English (facultatif)", {
            "classes": ("collapse",),
            "description": "Laisse vide : la version anglaise du site affichera le texte français.",
            "fields": ("titre_en", "resume_en", "corps_en"),
        }),
    )

    @admin.display(description="lecture")
    def lecture(self, obj):
        return obj.pour_gabarit()["lecture"]["fr"]

    @admin.display(description="sur le site")
    def voir(self, obj):
        # Publié : lien vers le site public. Brouillon : aperçu dans le back-office.
        if obj.publie:
            url = settings.PUBLIC_URL + f"/articles/{obj.slug}/"
            return format_html('<a href="{}" target="_blank" rel="noopener">voir en ligne →</a>', url)
        return format_html('<a href="{}" target="_blank">aperçu du brouillon →</a>', obj.get_absolute_url())

    @admin.action(description="Publier les articles sélectionnés")
    def publier(self, request, queryset):
        self.message_user(request, f"{queryset.update(publie=True)} article(s) publié(s).")

    @admin.action(description="Repasser en brouillon")
    def depublier(self, request, queryset):
        self.message_user(request, f"{queryset.update(publie=False)} article(s) repassé(s) en brouillon.")


@admin.register(Sujet)
class SujetAdmin(admin.ModelAdmin):
    list_display = ("nom_fr", "nom_en", "famille", "nb_articles")
    list_filter = ("famille",)

    @admin.display(description="articles")
    def nb_articles(self, obj):
        return obj.article_set.count()


# ===== VISITES =====
def _top(qs, champ, n=8):
    return list(qs.exclude(**{champ: ""}).values(champ).annotate(n=Count("id")).order_by("-n")[:n])


@admin.register(Visite)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ("date", "chemin", "source", "lieu", "appareil", "navigateur", "systeme")
    list_filter = ("date", "pays", "source", "appareil", "navigateur", "systeme")
    search_fields = ("chemin", "source", "ville", "referent")
    date_hierarchy = "date"
    list_per_page = 50
    change_list_template = "admin/core/visite/change_list.html"

    @admin.display(description="lieu", ordering="pays")
    def lieu(self, obj):
        morceaux = [m for m in (obj.ville, obj.region if obj.region != obj.ville else "") if m]
        detail = ", ".join(morceaux)
        return f"{drapeau(obj.pays)} {obj.pays}" + (f" · {detail}" if detail else "") if obj.pays else "—"

    # Le journal est en lecture seule : pas d'ajout ni de modification à la main.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        reponse = super().changelist_view(request, extra_context)
        try:
            qs = reponse.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return reponse
        maintenant = timezone.now()
        externes = qs.exclude(source="Navigation interne")
        par_jour = (qs.filter(date__gte=maintenant - timedelta(days=30))
                    .annotate(jour=TruncDate("date")).values("jour")
                    .annotate(n=Count("id"), uniques=Count("visiteur", distinct=True)).order_by("jour"))
        par_jour = list(par_jour)
        maxi = max([j["n"] for j in par_jour] or [1])
        for j in par_jour:
            j["pct"] = round(100 * j["n"] / maxi)
        pays = _top(qs, "pays")
        for p in pays:
            p["drapeau"] = drapeau(p["pays"])
        jeton = signing.dumps("ne-pas-compter", salt="portfolio.visites")
        reponse.context_data["lien_ne_pas_compter"] = f"{settings.PUBLIC_URL}/ne-pas-compter/{jeton}/"
        reponse.context_data["stats"] = {
            "vues": qs.count(),
            "visiteurs": qs.values("visiteur").distinct().count(),
            "aujourdhui": qs.filter(date__date=timezone.localdate()).count(),
            "semaine": qs.filter(date__gte=maintenant - timedelta(days=7)).count(),
            "par_jour": par_jour,
            "pays": pays,
            "sources": _top(externes, "source"),
            "pages": _top(qs, "chemin"),
            "appareils": _top(qs, "appareil", 3),
            "villes": _top(qs, "ville"),
        }
        return reponse


# ===== MESSAGES DE CONTACT =====
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("date", "nom", "email", "apercu", "lieu", "email_envoye", "lu")
    list_display_links = ("date", "nom")
    list_filter = ("lu", "email_envoye", "date", "langue")
    search_fields = ("nom", "email", "message")
    list_editable = ("lu",)
    readonly_fields = ("date", "nom", "email", "message", "langue", "pays", "ville", "email_envoye", "repondre")
    fields = ("date", "nom", "email", "repondre", "message", "langue", "pays", "ville", "email_envoye", "lu")
    actions = ["marquer_lus"]

    def has_add_permission(self, request):
        return False

    @admin.display(description="message")
    def apercu(self, obj):
        return obj.message[:80] + ("…" if len(obj.message) > 80 else "")

    @admin.display(description="lieu")
    def lieu(self, obj):
        return f"{drapeau(obj.pays)} {obj.ville or obj.pays}".strip() or "—"

    @admin.display(description="répondre")
    def repondre(self, obj):
        return format_html('<a href="mailto:{}?subject=Re%C2%A0%3A%20votre%20message">Répondre par email →</a>', obj.email)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        Message.objects.filter(pk=object_id, lu=False).update(lu=True)  # ouvert = lu
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.action(description="Marquer comme lus")
    def marquer_lus(self, request, queryset):
        queryset.update(lu=True)


# ===== JOURNAL DES CONNEXIONS (sécurité) =====
@admin.register(Connexion)
class ConnexionAdmin(admin.ModelAdmin):
    list_display = ("date", "resultat", "identifiant", "ip", "lieu", "navigateur_court")
    list_filter = ("reussie", "date")
    search_fields = ("identifiant", "ip")
    date_hierarchy = "date"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="résultat", boolean=True, ordering="reussie")
    def resultat(self, obj):
        return obj.reussie

    @admin.display(description="lieu")
    def lieu(self, obj):
        return f"{drapeau(obj.pays)} {obj.ville or obj.pays}".strip() or "—"

    @admin.display(description="navigateur")
    def navigateur_court(self, obj):
        return obj.navigateur[:70]
