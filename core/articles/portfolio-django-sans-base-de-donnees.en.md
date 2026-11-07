My first portfolio was a static HTML page hosted on GitHub Pages. It did the job, but every change
meant editing the HTML in two places (French and English), and nothing was computed: figures and
technology lists were copied by hand. I moved it to **Django**, the Python framework I already use,
keeping the same theme.

## No database

A portfolio doesn't need PostgreSQL. The content changes a few times a month and I'm the one writing
it. So I put **all the content in a Python file**, `core/content.py`, as lists and dictionaries:

```python
def t(fr, en=None):
    """Bilingual text (same text in both languages if en is omitted)."""
    return {"fr": fr, "en": en if en is not None else fr}

PROJETS_ING = [
    {
        "titre": t("Plateforme CENETI", "CENETI Platform"),
        "tech": ["Laravel", "PHP", "PostgreSQL", "SQL", "Docker"],
        # ...
    },
]
```

In the settings, `DATABASES = {}` and only two apps are installed: `staticfiles` and mine. No
migrations, no database server to host, and the content is versioned with Git like the rest of the
code.

## Data, so computations

The point of going through Python is that the content becomes **data you can process**. The skills ×
projects matrix on the home page isn't written anywhere: the view computes it from each project's
tech stack.

```python
from collections import Counter

usage = Counter(tech for p in projets for tech in p["tech"])
lignes = [
    {"tech": tech, "nb": nb, "cellules": [tech in p["tech"] for p in projets]}
    for tech, nb in sorted(usage.items(), key=lambda kv: (-kv[1], kv[0].lower()))
]
```

Same idea for the project overview, the "N of 5 projects" bars and this article's reading time: I add
a project to `content.py` and everything else follows.

## Two languages without reloading

Every text is rendered twice in the HTML, tagged with a `data-lang` attribute. A tiny Django template
takes care of it:

```html
<span data-lang="fr">{{ t.fr }}</span><span data-lang="en" hidden>{{ t.en }}</span>
```

The FR/EN button toggles the `hidden` attribute in JavaScript and remembers the choice in
`localStorage`. One detail cost me some time: inside SVG charts, `<tspan>` elements have no `hidden`
property. You need `el.toggleAttribute("hidden", ...)`, which works everywhere.

## Django on Vercel

Vercel can run a Python WSGI app with `@vercel/python`. Three things are enough:

1. A `vercel.json` that sends every request to `portfolio_site/wsgi.py`.
2. In `wsgi.py`, a variable named `app`, since that's the name Vercel looks for:
   `app = application`.
3. **WhiteNoise** for static files. Since there is no `collectstatic` step,
   `WHITENOISE_USE_FINDERS = True` makes it read files straight from `core/static/`.

```json
{
  "builds": [{ "src": "portfolio_site/wsgi.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "portfolio_site/wsgi.py" }]
}
```

Production settings come from environment variables. `DEBUG` is turned off as soon as the `VERCEL`
variable exists, and `ALLOWED_HOSTS` accepts `.vercel.app`. Every push to the production branch
redeploys the site.

## Takeaway

The site stays as light as a static page, but the content became a single source of data from which
everything else is derived. For a data profile, that's consistent: **write the facts once, compute
the rest**.
