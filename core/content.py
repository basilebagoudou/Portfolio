"""Contenu du portfolio, dans les deux langues.

Chaque texte traduit est un dict {"fr": ..., "en": ...}. Pour ajouter un projet,
une compétence ou une étape de parcours, il suffit de modifier les listes
ci-dessous : le gabarit core/index.html les affiche automatiquement.
"""


def t(fr, en=None):
    """Texte bilingue (même texte dans les deux langues si en est omis)."""
    return {"fr": fr, "en": en if en is not None else fr}


PARCOURS = [
    {
        "periode": t("2026 – 2027"),
        "titre": t("Licence 3 — Génie Logiciel et Systèmes d'information",
                   "3rd-year Bachelor — Software Engineering & Information Systems"),
        "lieu": t("Institut Africain d'Informatique (IAI), Togo",
                  "African Institute of Computer Science (IAI), Togo"),
        "texte": t("Conception de structures de données, bases de données, génie logiciel, "
                   "programmation orientée objet.",
                   "Data structures, databases, software engineering, object-oriented "
                   "programming."),
        "en_cours": True,
    },
    {
        "periode": t("Sept. – déc. 2026", "Sep – Dec 2026"),
        "titre": t("GCI World 2026 — Data Science", "GCI World 2026 — Data Science"),
        "lieu": t("Matsuo-Iwasawa Lab, Université de Tokyo (en ligne)",
                  "Matsuo-Iwasawa Lab, The University of Tokyo (online)"),
        "texte": t("Programme international de data science : NumPy, pandas, Matplotlib, "
                   "apprentissage supervisé, évaluation de modèles, feature engineering, "
                   "et une compétition de machine learning.",
                   "International data science program: NumPy, pandas, Matplotlib, "
                   "supervised learning, model evaluation, feature engineering, and a "
                   "machine learning competition."),
        "en_cours": True,
    },
    {
        "periode": t("Automne 2026", "Fall 2026"),
        "titre": t("CS50P — Introduction à la programmation en Python",
                   "CS50P — Introduction to Programming with Python"),
        "lieu": t("Université Harvard (en ligne)", "Harvard University (online)"),
        "texte": t("Fonctions, structures de contrôle, exceptions, bibliothèques, tests "
                   "unitaires, entrées/sorties de fichiers, expressions régulières, POO.",
                   "Functions, control flow, exceptions, libraries, unit tests, file I/O, "
                   "regular expressions, OOP."),
        "en_cours": True,
    },
    {
        "periode": t("Stage", "Internship"),
        "titre": t("Développeur full-stack — CENETI", "Full-stack developer — CENETI"),
        "lieu": t("Lomé, Togo"),
        "texte": t("Conception et mise en production d'une plateforme Laravel complète : "
                   "site vitrine, back-office multi-rôles, base PostgreSQL, Docker.",
                   "Designed and shipped a complete Laravel platform: public site, "
                   "role-based back-office, PostgreSQL database, Docker."),
        "en_cours": False,
    },
]

# Sessions GCI World 2026 actuellement suivies (modules 1 à 9).
GCI_MODULES = [
    {"num": 1, "titre": t("Introduction à la data science", "Introduction to Data Science")},
    {"num": 2, "titre": t("Manipuler des données avec NumPy", "Manipulating Data with NumPy")},
    {"num": 3, "titre": t("Nettoyer des données avec pandas", "Cleaning Data with pandas")},
    {"num": 4, "titre": t("Visualiser avec Matplotlib", "Visualizing with Matplotlib")},
    {"num": 5, "titre": t("Apprentissage supervisé", "Supervised Learning")},
    {"num": 6, "titre": t("Évaluation de modèles", "Model Evaluation")},
    {"num": 7, "titre": t("Compétition & projet final", "Competition & Final Assignment")},
    {"num": 8, "titre": t("Feature engineering", "Feature Engineering")},
    {"num": 9, "titre": t("Marketing et data science", "Marketing & Data Science")},
]

COMPETENCES = [
    {
        "titre": t("Data & IA", "Data & AI"),
        "accent": True,
        "items": ["Python", "NumPy", "pandas", "Matplotlib", "seaborn", "scikit-learn",
                  "Jupyter", t("Statistiques", "Statistics")],
    },
    {
        "titre": t("Développement web", "Web development"),
        "items": ["Django", "Laravel", "PHP", "JavaScript", "HTML / CSS"],
    },
    {
        "titre": t("Bases de données", "Databases"),
        "items": ["SQL", "PostgreSQL", "MySQL"],
    },
    {
        "titre": t("Outils", "Tools"),
        "items": ["Git / GitHub", "Docker", "Linux", "VS Code"],
    },
]

PROJETS = [
    {
        "titre": t("Home Credit — Risque de défaut", "Home Credit — Default Risk"),
        "tag": t("Data · en cours", "Data · ongoing"),
        "data": True,
        "texte": t("Compétition de machine learning du programme GCI : prédire la probabilité "
                   "qu'un client fasse défaut sur son crédit. Exploration et nettoyage des "
                   "données clients, feature engineering, entraînement et validation de "
                   "modèles de classification.",
                   "Machine learning competition from the GCI program: predict the "
                   "probability that a client defaults on their loan. Client data "
                   "exploration and cleaning, feature engineering, training and validating "
                   "classification models."),
        "tech": ["Python", "pandas", "scikit-learn", "Jupyter"],
        "liens": [],
    },
    {
        "titre": t("Plateforme CENETI", "CENETI Platform"),
        "tag": t("Stage", "Internship"),
        "texte": t("Plateforme web complète pour le CENETI (Togo) : site vitrine public et "
                   "back-office sécurisé multi-rôles (gestion des campagnes, candidatures, "
                   "messagerie interne). Conçue et déployée de bout en bout, du schéma de "
                   "base de données au déploiement en production.",
                   "Complete web platform for CENETI (Togo): public site and a role-based "
                   "secured back-office (campaign management, applications, internal "
                   "messaging). Designed and deployed end-to-end, from database schema to "
                   "production."),
        "tech": ["Laravel", "Blade", "PostgreSQL", "Docker"],
        "liens": [{"url": "https://ceneti-production.up.railway.app",
                   "label": t("Voir le site", "View site")}],
    },
    {
        "titre": t("Optima"),
        "tag": t("Desktop"),
        "texte": t("Application desktop pour partager la connexion mobile d'un téléphone en "
                   "Wi-Fi depuis un PC Linux, en contournant la détection de partage de "
                   "connexion (« tethering ») des opérateurs.",
                   "Desktop app to share a phone's mobile data as Wi-Fi from a Linux PC, "
                   "bypassing carrier tethering detection."),
        "tech": ["Python", "Tkinter", "Shell", "Linux"],
        "liens": [{"url": "https://github.com/basilebagoudou/optima", "label": t("GitHub")}],
    },
    {
        "titre": t("Site d'un coffee shop", "Coffee shop website"),
        "tag": t("Web"),
        "texte": t("Site vitrine responsive pour un coffee shop à Lomé, en HTML, CSS et "
                   "JavaScript pur, avec animations CSS.",
                   "Responsive showcase website for a coffee shop in Lomé, built with plain "
                   "HTML, CSS and JavaScript, with CSS animations."),
        "tech": ["HTML", "CSS", "JavaScript"],
        "liens": [{"url": "https://github.com/basilebagoudou/Coffe_website",
                   "label": t("GitHub")}],
    },
]
