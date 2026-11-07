# Portfolio

Personal portfolio of **Basile Bagoudou** — 3rd-year Software Engineering student at
IAI Togo, focused on data science. Bilingual (French/English) single-page site built
with **Django** and deployed on **Vercel**: https://basile-bagoudou.vercel.app

## Sections

| Section | Content |
|---------|---------|
| Hero | Headline, value proposition, availability, `profil.ipynb` card (`bb.describe()`) |
| Key figures | Animated counters: dataset sizes, GCI modules followed, number of projects |
| Profile | What I bring to a data team (analyze, model, ship) + data workflow pipeline |
| Projects | Data case studies (context / approach / real challenge, with charts) + engineering projects |
| Skills | Skill groups + a skills × projects matrix computed from the project data |
| Journey | Timeline (L3 at IAI, GCI World 2026, CS50P, CENETI) + GCI modules followed |
| Contact | Internship pitch, email, GitHub, LinkedIn + contact form (sent by email) |
| `/articles/` | Articles list; each article at `/articles/<slug>/` |

## Project structure

```
Portfolio/
├── manage.py
├── vercel.json              # Vercel: every request goes to the Django WSGI app
├── requirements.txt
├── portfolio_site/          # Django project (settings, urls, wsgi)
└── core/                    # the portfolio app
    ├── content.py           # ALL the content (FR + EN) — edit this to update the site
    ├── articles/            # article bodies in Markdown: <slug>.fr.md / <slug>.en.md
    ├── articles.py          # loads + renders the articles (reading time, dates)
    ├── forms.py             # contact form (honeypot + signed timestamp against spam)
    ├── views.py             # computes key figures and the skills × projects matrix
    ├── templates/core/      # index.html + _t.html (bilingual text helper)
    └── static/core/         # style.css, script.js
```

There is no database: the content lives in `core/content.py` as Python data. Each
translated text is a `{"fr": ..., "en": ...}` pair built with the `t()` helper.

## Writing an article

1. Add an entry to `ARTICLES` in `core/content.py` (slug, date, title, summary, topics, project).
2. Write `core/articles/<slug>.fr.md` and `core/articles/<slug>.en.md`.

The reading time is computed from the text; the list is sorted by date.

## How the translation system works

Every translatable text is rendered twice, tagged with `data-lang`:

```html
<span data-lang="fr">À propos</span>
<span data-lang="en" hidden>About</span>
```

`script.js` shows one language by toggling `hidden`, updates `<html lang>` and stores the
choice in `localStorage` (`langue-portfolio`). French is the default.

## Running it locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver
# → http://127.0.0.1:8000
```

## Deployment (Vercel)

`vercel.json` routes every request to `portfolio_site/wsgi.py` (`@vercel/python`).
Static files are served by WhiteNoise straight from `core/static/`, so no build step
is needed. Optional environment variables:

| Variable | Purpose |
|----------|---------|
| `DJANGO_SECRET_KEY` | Secret key (recommended) |
| `DJANGO_ALLOWED_HOSTS` | Extra hosts, e.g. a custom domain (comma-separated) |
| `DJANGO_DEBUG` | `1` to enable debug (never in production) |
| `EMAIL_HOST_USER` | Gmail address that sends the contact-form emails |
| `EMAIL_HOST_PASSWORD` | Google **app password** for that address (required for the form) |
| `CONTACT_EMAIL` | Where messages are delivered (default: basile2bagoudou@gmail.com) |

Locally (debug on, no password set), contact messages are printed in the terminal.
