"""Contenu du portfolio, dans les deux langues.

Chaque texte traduit est un dict {"fr": ..., "en": ...} construit avec t().
Pour mettre le site à jour, il suffit de modifier les listes ci-dessous : le
gabarit core/index.html les affiche, et core/views.py en dérive les chiffres
clés et la matrice compétences × projets.

Règle : uniquement des faits vérifiables (pas de score inventé, pas de
« niveau » de compétence en pourcentage).
"""


def t(fr, en=None):
    """Texte bilingue (même texte dans les deux langues si en est omis)."""
    return {"fr": fr, "en": en if en is not None else fr}


# Carte « basile.describe() » du hero.
PROFIL = [
    (t("rôle", "role"), t("Élève ingénieur en data", "Data engineering student")),
    (t("école", "school"), t("IAI Togo — L3 Génie Logiciel", "IAI Togo — 3rd year, Software Eng.")),
    (t("formation+", "extra"), t("GCI World 2026 (U. Tokyo) · CS50P (Harvard)",
                                 "GCI World 2026 (U. Tokyo) · CS50P (Harvard)")),
    (t("analyse", "analysis"), t("Python · pandas · NumPy · SQL")),
    (t("modèles", "models"), t("scikit-learn · validation croisée · ROC AUC",
                               "scikit-learn · cross-validation · ROC AUC")),
    (t("livraison", "shipping"), t("Django · PostgreSQL · Docker")),
    (t("dispo", "available"), t("Stage — mai 2027", "Internship — May 2027")),
]

# Ce que j'apporte à une équipe data.
APPORTS = [
    {
        "icone": "analyse",
        "titre": t("Analyser et nettoyer", "Analyze & clean"),
        "texte": t("Je prends un jeu de données brut — valeurs manquantes, types incohérents, "
                   "variables mal encodées — et je le rends exploitable avec pandas. Puis "
                   "j'explore : distributions, corrélations, visualisations qui racontent "
                   "quelque chose.",
                   "I take a raw dataset — missing values, inconsistent types, badly encoded "
                   "features — and make it usable with pandas. Then I explore: distributions, "
                   "correlations, charts that actually tell something."),
    },
    {
        "icone": "modele",
        "titre": t("Modéliser et évaluer", "Model & evaluate"),
        "texte": t("Classification, régression, feature engineering. Surtout, je sais "
                   "évaluer honnêtement : jeu de validation séparé, validation croisée, "
                   "métriques adaptées (ROC AUC sur des classes déséquilibrées plutôt "
                   "qu'une accuracy trompeuse).",
                   "Classification, regression, feature engineering. Above all, I evaluate "
                   "honestly: held-out validation, cross-validation, the right metric (ROC AUC "
                   "on imbalanced classes rather than misleading accuracy)."),
    },
    {
        "icone": "livrer",
        "titre": t("Livrer en production", "Ship to production"),
        "texte": t("Mon profil de génie logiciel est un atout : SQL, Git, Docker, back-end "
                   "Django et Laravel. J'ai déjà mis une plateforme complète en production — "
                   "un modèle n'a de valeur que s'il est utilisé.",
                   "My software engineering background is an asset: SQL, Git, Docker, Django "
                   "and Laravel back-ends. I've already shipped a complete platform to "
                   "production — a model only has value once it's used."),
    },
]

# Démarche data, de la donnée brute à la mise en production.
PIPELINE = [
    {"etape": t("Collecter", "Collect"), "outils": "SQL · CSV · API"},
    {"etape": t("Nettoyer", "Clean"), "outils": "pandas · NumPy"},
    {"etape": t("Explorer", "Explore"), "outils": "Matplotlib · seaborn"},
    {"etape": t("Modéliser", "Model"), "outils": "scikit-learn"},
    {"etape": t("Évaluer", "Evaluate"), "outils": "CV · ROC AUC"},
    {"etape": t("Déployer", "Deploy"), "outils": "Django · Docker"},
]

PROJETS_DATA = [
    {
        "titre": t("Home Credit — prédiction du risque de défaut",
                   "Home Credit — loan default prediction"),
        "statut": t("Compétition ML · en cours", "ML competition · ongoing"),
        "viz": "desequilibre",
        "faits": [
            {"valeur": "171 202", "valeur_en": "171,202", "label": t("clients", "clients")},
            {"valeur": "32", "label": t("variables", "features")},
            {"valeur": "8,1 %", "valeur_en": "8.1%", "label": t("de défauts", "defaults")},
        ],
        "contexte": t("Compétition du programme GCI World 2026 (Université de Tokyo), "
                      "inspirée du challenge Kaggle « Home Credit Default Risk » : estimer la "
                      "probabilité qu'un client ne rembourse pas son crédit.",
                      "Competition from the GCI World 2026 program (University of Tokyo), based "
                      "on Kaggle's “Home Credit Default Risk”: estimate the probability that a "
                      "client won't repay their loan."),
        "approche": t("Exploration et nettoyage des données clients, encodage des variables "
                      "catégorielles, feature engineering, puis comparaison de modèles de "
                      "classification en validation croisée.",
                      "Client data exploration and cleaning, categorical encoding, feature "
                      "engineering, then comparing classification models with "
                      "cross-validation."),
        "enjeu": t("Seuls 8,1 % des clients font défaut : une accuracy de 92 % ne prouve "
                   "rien. Le classement se fait sur la ROC AUC, qui mesure la capacité à "
                   "ordonner les clients par risque.",
                   "Only 8.1% of clients default: 92% accuracy proves nothing. Ranking uses "
                   "ROC AUC, which measures how well clients are ordered by risk."),
        "tech": ["Python", "pandas", "scikit-learn", "Matplotlib", "Jupyter"],
        "liens": [],
    },
    {
        "titre": t("Opérateur télécom — proposition business data-driven",
                   "Telecom operator — data-driven business proposal"),
        "statut": t("Projet final · en cours", "Final project · ongoing"),
        "viz": "tables",
        "faits": [
            {"valeur": "100 000", "valeur_en": "100,000", "label": t("abonnés", "subscribers")},
            {"valeur": "2", "label": t("tables jointes", "joined tables")},
            {"valeur": "~100", "label": t("variables", "features")},
        ],
        "contexte": t("Mise en situation de consultant data pour un opérateur télécom : "
                      "identifier le vrai problème business à partir de ses données clients "
                      "et d'usage.",
                      "Acting as a data consultant for a telecom operator: identify the real "
                      "business problem from its customer and usage data."),
        "approche": t("Analyse exploratoire de deux tables (profil client et historique "
                      "d'usage), au moins un modèle de machine learning, puis une "
                      "proposition chiffrée (gain de revenu, réduction de coûts ou de risque).",
                      "Exploratory analysis of two tables (customer profile and usage "
                      "history), at least one machine learning model, then a quantified "
                      "proposal (revenue lift, cost savings or risk reduction)."),
        "enjeu": t("Passer d'un modèle à une décision : présenter en 15 slides maximum un "
                   "impact business chiffré, compréhensible par un client non technique.",
                   "Going from a model to a decision: present a quantified business impact in "
                   "15 slides max, understandable by a non-technical client."),
        "tech": ["Python", "pandas", "scikit-learn", "seaborn", "Jupyter"],
        "liens": [],
    },
]

PROJETS_ING = [
    {
        "titre": t("Plateforme CENETI", "CENETI Platform"),
        "tag": t("Stage · en production", "Internship · in production"),
        "texte": t("Plateforme web complète conçue et déployée de bout en bout pendant mon stage : site "
                   "public et back-office multi-rôles (campagnes, candidatures, messagerie "
                   "interne). Du schéma PostgreSQL à la mise en production avec Docker.",
                   "Complete web platform I designed and shipped end-to-end during my "
                   "internship: public site and role-based back-office (campaigns, "
                   "applications, internal messaging). From the PostgreSQL schema to "
                   "production with Docker."),
        "tech": ["Laravel", "PHP", "PostgreSQL", "SQL", "Docker"],
        "liens": [{"url": "https://ceneti-production.up.railway.app",
                   "label": t("Voir le site", "View site")}],
    },
    {
        "titre": t("Optima"),
        "tag": t("Desktop · Linux"),
        "texte": t("Application desktop qui transforme un PC Linux en point d'accès Wi-Fi "
                   "pour partager la connexion mobile d'un téléphone : interface graphique, "
                   "gestion des appareils connectés, scripts système.",
                   "Desktop app that turns a Linux PC into a Wi-Fi hotspot to share a phone's "
                   "mobile data: GUI, connected-device management, system scripts."),
        "tech": ["Python", "Tkinter", "Shell", "Linux"],
        "liens": [{"url": "https://github.com/basilebagoudou/optima", "label": t("GitHub")}],
    },
    {
        "titre": t("Ce portfolio", "This portfolio"),
        "tag": t("Web · Django"),
        "texte": t("Site bilingue en Django, déployé sur Vercel. Le contenu est stocké comme "
                   "données Python ; les chiffres clés et la matrice compétences × projets "
                   "ci-dessous en sont calculés automatiquement.",
                   "Bilingual Django site deployed on Vercel. Content is stored as Python "
                   "data; the key figures and the skills × projects matrix below are "
                   "computed from it automatically."),
        "tech": ["Python", "Django", "Git"],
        "liens": [{"url": "https://github.com/basilebagoudou/Portfolio",
                   "label": t("Code source", "Source code")}],
    },
]

PARCOURS = [
    {
        "periode": t("2026 – 2027"),
        "titre": t("Licence 3 — Génie Logiciel et Systèmes d'information",
                   "3rd-year Bachelor — Software Engineering & Information Systems"),
        "lieu": t("Institut Africain d'Informatique (IAI), Togo",
                  "African Institute of Computer Science (IAI), Togo"),
        "texte": t("Structures de données, bases de données, génie logiciel, programmation "
                   "orientée objet, statistiques.",
                   "Data structures, databases, software engineering, object-oriented "
                   "programming, statistics."),
        "en_cours": True,
    },
    {
        "periode": t("Sept. – déc. 2026", "Sep – Dec 2026"),
        "titre": t("GCI World 2026 — Data Science"),
        "lieu": t("Matsuo-Iwasawa Lab, Université de Tokyo (en ligne)",
                  "Matsuo-Iwasawa Lab, The University of Tokyo (online)"),
        "texte": t("Programme international : NumPy, pandas, visualisation, "
                   "apprentissage supervisé, évaluation de modèles, feature engineering, "
                   "data science appliquée au marketing, SQL, apprentissage non supervisé, "
                   "séries temporelles, compétition de machine learning.",
                   "International program: NumPy, pandas, visualization, supervised "
                   "learning, model evaluation, feature engineering, data science for "
                   "marketing, SQL, unsupervised learning, time series, machine learning "
                   "competition."),
        "en_cours": True,
    },
    {
        "periode": t("Automne 2026", "Fall 2026"),
        "titre": t("CS50P — Programmer en Python", "CS50P — Programming with Python"),
        "lieu": t("Université Harvard (en ligne)", "Harvard University (online)"),
        "texte": t("Python solide : fonctions, exceptions, tests unitaires, fichiers, "
                   "expressions régulières, programmation orientée objet.",
                   "Solid Python: functions, exceptions, unit tests, file I/O, regular "
                   "expressions, object-oriented programming."),
        "en_cours": True,
    },
    {
        "periode": t("Stage", "Internship"),
        "titre": t("Développeur full-stack — CENETI", "Full-stack developer — CENETI"),
        "lieu": t("Lomé, Togo"),
        "texte": t("Conception et mise en production d'une plateforme Laravel / PostgreSQL "
                   "complète, du schéma de données à la production.",
                   "Designed and shipped a complete Laravel / PostgreSQL platform, "
                   "from data schema to production."),
        "en_cours": False,
    },
]

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
    {"num": 10, "titre": t("SQL")},
    {"num": 11, "titre": t("Apprentissage non supervisé", "Unsupervised Learning")},
    {"num": 12, "titre": t("Analyse de séries temporelles", "Time Series Analysis")},
    {"num": 13, "titre": t("Session invitée", "Guest Session")},
    {"num": 14, "titre": t("Contenus spéciaux", "Special Contents")},
]

COMPETENCES = [
    {
        "titre": t("Data & machine learning", "Data & machine learning"),
        "accent": True,
        "items": ["Python", "pandas", "NumPy", "scikit-learn", "Matplotlib", "seaborn",
                  "Jupyter", t("Statistiques", "Statistics")],
    },
    {
        "titre": t("Bases de données", "Databases"),
        "items": ["SQL", "PostgreSQL", "MySQL"],
    },
    {
        "titre": t("Ingénierie & déploiement", "Engineering & deployment"),
        "items": ["Django", "Laravel", "PHP", "JavaScript", "Docker", "Git", "Linux"],
    },
]
