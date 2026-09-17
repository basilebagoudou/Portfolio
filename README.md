# Portfolio

Personal portfolio of **Basile Bagoudou** — software engineering student at IAI Togo.
A static, bilingual (French/English) single-page site built with plain HTML, CSS and
JavaScript, with no framework and no build step.

**Live:** [basilebagoudou.github.io/Portfolio](https://basilebagoudou.github.io/Portfolio/)

## Sections

| Section | Content |
|---------|---------|
| Hero | Name, current studies, short pitch, calls to action |
| About | Background, CENETI internship, key details (education, university, email, availability) |
| Skills | Languages (PHP, JavaScript, Python), Web (HTML, CSS), Databases (MySQL, PostgreSQL), Tools (Git, GitHub, VS Code, Linux) |
| Projects | CENETI Platform, Optima, and a showcase website, each with its stack and links |
| Contact | Email, GitHub and LinkedIn links |

## Features

- **Bilingual FR/EN** with a two-option switch in the navbar; the choice is remembered
between visits
- **Sticky header** that changes appearance once the page is scrolled past 50px
- **Reveal on scroll** — sections fade in through an `IntersectionObserver`
- **Mobile menu** — burger navigation that closes itself when a link is clicked
- **Responsive** layout, [Jost](https://fonts.google.com/specimen/Jost) from Google Fonts

## How the translation system works

There is no i18n library. Every translatable element exists twice in `index.html`,
tagged with a `data-lang` attribute:

```html
<span data-lang="fr">À propos</span>
<span data-lang="en" hidden>About</span>
```

`script.js` shows one language by toggling the `hidden` attribute on every `[data-lang]`
element, updates `<html lang>`, and stores the choice in `localStorage` under the
`langue-portfolio` key. French is the default on a first visit.

**When adding content, always add both versions** — an element with only a `data-lang="fr"`
variant disappears entirely when the visitor switches to English.

## Project structure

```
Portfolio/
├── index.html   # all the content, both languages
├── style.css    # styles, animations, responsive breakpoints
└── script.js    # sticky header, scroll reveal, mobile menu, language switch
```

## Running it locally

No dependencies to install — open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

A local server is preferable to opening the file directly, since `localStorage`
behaves more reliably over `http://` than over `file://`.

## Deployment

Published with GitHub Pages from the `main` branch. Any push to `main` updates the
live site within a minute or so.
