"""Formulaire de contact (sans base de données : le message part par email)."""
import time

from django import forms
from django.core import signing

# Anti-spam sans captcha : un champ piège invisible (« societe ») que seuls les
# robots remplissent, et un horodatage signé à l'affichage de la page. Un
# message envoyé moins de 3 s après l'affichage, ou plus de 24 h après, est
# refusé.
DELAI_MIN = 3
DELAI_MAX = 24 * 3600
SEL = "portfolio.contact"


def jeton_horodatage():
    return signing.dumps(int(time.time()), salt=SEL)


class ContactForm(forms.Form):
    nom = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=254)
    message = forms.CharField(min_length=10, max_length=5000)
    societe = forms.CharField(required=False)  # champ piège
    ts = forms.CharField()
    langue = forms.ChoiceField(choices=[("fr", "fr"), ("en", "en")], required=False)

    def est_robot(self):
        """Vrai si le message a l'air automatique (à ignorer silencieusement)."""
        if self.cleaned_data.get("societe"):
            return True
        try:
            debut = signing.loads(self.cleaned_data["ts"], salt=SEL, max_age=DELAI_MAX)
        except signing.BadSignature:
            return True
        return time.time() - debut < DELAI_MIN
