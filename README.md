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
├── portfolio_site/          # settings, urls.py (portfolio), urls_admin.py (back-office), wsgi
└── core/
    ├── content.py           # page content (FR + EN): profile, projects, skills, journey…
    ├── models.py            # Article, Sujet, Message, Visite, Connexion
    ├── admin.py             # back-office screens (+ visit stats)
    ├── admin_site.py        # admin site with login lockout
    ├── securite.py          # security headers, brute-force protection, rate limits
    ├── visites.py           # visit-logging middleware
    ├── views.py, forms.py, flux.py (RSS), projets.py
    ├── articles_initiaux/   # Markdown of the first two articles (seed migration only)
    ├── templates/           # core/ (site) + admin/ (back-office overrides)
    └── static/core/         # style.css, script.js, admin.css
```

Page content lives in `core/content.py` as Python data (each translated text is a
`{"fr": ..., "en": ...}` pair built with `t()`). Articles, messages and visits live in the
database and are managed in the back-office.

## Two sites, one codebase

`SITE_ROLE` decides which site runs. They share the same database.

| Role | Locally | In production | Content |
|------|---------|---------------|---------|
| `public` (default) | `python manage.py runserver 8000` | https://basile-bagoudou.vercel.app | The portfolio. No admin URLs at all. |
| `admin` | `SITE_ROLE=admin python manage.py runserver 8001` | separate Vercel project | Back-office: articles, contact messages, visits, login log; `/apercu/` previews the site with drafts. |

## Back-office

- **Articles**: written in Markdown in the Django admin (French required, English optional and
  falls back to French). Unchecked "publié" = draft, visible only in `/apercu/`.
- **Messages**: every contact-form message is stored (and emailed if SMTP is configured).
- **Visites**: page views with country/region/city (Vercel geo headers), source (Referer or
  `utm_source`), device, browser, OS, plus a stats panel. No IP address is stored: a daily salted
  hash counts unique visitors. Bots, Do Not Track/GPC, logged-in users and browsers opted out via
  the link in the stats panel are not logged. Visits older than 13 months are purged.
- **Connexions**: log of every back-office login attempt.

## Security

- Back-office on a separate host; the public site has no admin routes.
- Login lockout: 5 failures per IP (or 30 overall) in 15 minutes → blocked (HTTP 429).
- Passwords: 12 characters minimum + Django's validators. Sessions: 8 h max, end with the browser.
- HTTPS redirect, HSTS, `Secure`/`HttpOnly`/`SameSite` cookies, CSRF on every form.
- Headers: Content-Security-Policy (no inline scripts), `X-Frame-Options: DENY`,
  Permissions-Policy, Referrer-Policy, COOP; back-office also sends `noindex` + `no-store`.
- Contact form: honeypot, signed timestamp, 5 messages per hour per visitor.
- `DJANGO_SECRET_KEY` is mandatory for the back-office.

## Writing an article

Log in to the back-office → Articles → Ajouter. The reading time, the card and the RSS feed
(`/articles/rss/`) and `sitemap.xml` follow automatically.

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
.venv/bin/python manage.py migrate            # local SQLite database (db.sqlite3)
.venv/bin/python manage.py createsuperuser    # back-office account
.venv/bin/python manage.py runserver 8000                  # portfolio
SITE_ROLE=admin .venv/bin/python manage.py runserver 8001  # back-office
```

## Deployment (Vercel)

`vercel.json` routes every request to `portfolio_site/wsgi.py` (`@vercel/python`); WhiteNoise
serves static files. On each cold start, `wsgi.py` applies migrations and (back-office only)
creates the admin account from the environment if it doesn't exist yet.

Two Vercel projects deploy the same repo and branch (`django`):

| Variable | Portfolio project | Back-office project |
|----------|:-:|:-:|
| `DATABASE_URL` (Postgres, e.g. Neon via Vercel Storage) | ✓ | ✓ |
| `DJANGO_SECRET_KEY` (same value on both) | ✓ | ✓ |
| `SITE_ROLE=admin` | | ✓ |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` | | ✓ |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` (Gmail app password, optional) | ✓ | |
| `PUBLIC_URL` (optional, default https://basile-bagoudou.vercel.app) | | ✓ |

Without `DATABASE_URL`, the portfolio runs on a temporary SQLite database in `/tmp` seeded with
the initial articles (nothing written there is kept).
