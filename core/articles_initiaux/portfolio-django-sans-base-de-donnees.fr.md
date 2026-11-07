Mon premier portfolio était une page HTML statique hébergée sur GitHub Pages. Il faisait le travail,
mais chaque modification demandait de toucher au HTML à deux endroits (français et anglais), et rien
n'était calculé : les chiffres et les listes de technologies étaient recopiés à la main. Je l'ai migré
vers **Django**, le framework Python que j'utilise déjà, en gardant le même thème.

## Pas de base de données

Un portfolio n'a pas besoin de PostgreSQL. Le contenu change quelques fois par mois et c'est moi qui
l'écris. J'ai donc mis **tout le contenu dans un fichier Python**, `core/content.py`, sous forme de
listes et de dictionnaires :

```python
def t(fr, en=None):
    """Texte bilingue (même texte dans les deux langues si en est omis)."""
    return {"fr": fr, "en": en if en is not None else fr}

PROJETS_ING = [
    {
        "titre": t("Plateforme CENETI", "CENETI Platform"),
        "tech": ["Laravel", "PHP", "PostgreSQL", "SQL", "Docker"],
        # ...
    },
]
```

Côté réglages, `DATABASES = {}` et seules deux applis sont installées : `staticfiles` et la mienne.
Pas de migrations, pas de serveur de base à héberger, et le contenu est versionné avec Git comme le
reste du code.

## Des données, donc des calculs

L'intérêt de passer par Python, c'est que le contenu devient **une donnée qu'on peut traiter**. La
matrice compétences × projets de la page d'accueil n'est écrite nulle part : la vue la calcule à
partir des technos de chaque projet.

```python
from collections import Counter

usage = Counter(tech for p in projets for tech in p["tech"])
lignes = [
    {"tech": tech, "nb": nb, "cellules": [tech in p["tech"] for p in projets]}
    for tech, nb in sorted(usage.items(), key=lambda kv: (-kv[1], kv[0].lower()))
]
```

Même principe pour la vue d'ensemble des projets, les barres « N projets sur 5 » ou le temps de
lecture de cet article : j'ajoute un projet dans `content.py`, tout le reste suit.

## Deux langues sans recharger la page

Chaque texte est rendu deux fois dans le HTML, avec un attribut `data-lang`. Un petit gabarit Django
s'en charge :

```html
<span data-lang="fr">{{ t.fr }}</span><span data-lang="en" hidden>{{ t.en }}</span>
```

Le bouton FR/EN bascule l'attribut `hidden` en JavaScript et mémorise le choix dans `localStorage`.
Un détail m'a coûté un moment : dans les graphiques SVG, les `<tspan>` n'ont pas de propriété
`hidden`. Il faut passer par `el.toggleAttribute("hidden", ...)`, qui marche partout.

## Django sur Vercel

Vercel sait exécuter une application Python WSGI avec `@vercel/python`. Trois choses suffisent :

1. Un `vercel.json` qui envoie toutes les requêtes vers `portfolio_site/wsgi.py`.
2. Dans `wsgi.py`, une variable nommée `app`, car c'est ce nom que Vercel cherche :
   `app = application`.
3. **WhiteNoise** pour les fichiers statiques. Comme il n'y a pas d'étape `collectstatic`,
   `WHITENOISE_USE_FINDERS = True` lui fait lire les fichiers directement dans `core/static/`.

```json
{
  "builds": [{ "src": "portfolio_site/wsgi.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "portfolio_site/wsgi.py" }]
}
```

Les réglages de production passent par des variables d'environnement. `DEBUG` est désactivé dès que
la variable `VERCEL` existe, et `ALLOWED_HOSTS` accepte `.vercel.app`. Chaque push sur la branche de
production redéploie le site.

## Bilan

Le site reste aussi léger qu'une page statique, mais le contenu est devenu une source de données
unique dont le reste se déduit. Pour un profil data, c'est cohérent : **on écrit les faits une fois,
on calcule le reste**.

*Mise à jour : depuis, le site a un back-office pour écrire ces articles. Il utilise une base
Postgres, servie sur une adresse séparée du portfolio. Le contenu des pages, lui, vit toujours dans
`content.py`.*
