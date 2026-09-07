
const header = document.querySelector('header');

window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// ===== APPARITION AU SCROLL =====
const sections = document.querySelectorAll('section');

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, {
    threshold: 0.1
});

sections.forEach(function(section) {
    observer.observe(section);
});

// ===== MENU MOBILE =====
const menuBtn = document.querySelector('.menu-btn');
const navLinks = document.querySelector('nav ul');

menuBtn.addEventListener('click', function() {
    navLinks.classList.toggle('open');
    menuBtn.classList.toggle('active');
});

// Fermer le menu quand on clique sur un lien
document.querySelectorAll('nav ul li a').forEach(function(link) {
    link.addEventListener('click', function() {
        navLinks.classList.remove('open');
        menuBtn.classList.remove('active');
    });
});

// ===== SÉLECTEUR DE LANGUE (FR/EN) =====
// Chaque élément traduit existe en double dans le HTML
// (<... data-lang="fr">/<... data-lang="en" hidden>) : on affiche une
// langue en basculant l'attribut "hidden", et on mémorise le choix pour
// les visites suivantes.
const langToggle = document.querySelector('.lang-toggle');
const CLE_LANGUE = 'langue-portfolio';

function appliquerLangue(langue) {
    document.querySelectorAll('[data-lang]').forEach(function(el) {
        el.hidden = el.dataset.lang !== langue;
    });
    document.documentElement.lang = langue;
    localStorage.setItem(CLE_LANGUE, langue);
}

const langueSauvegardee = localStorage.getItem(CLE_LANGUE) || 'fr';
appliquerLangue(langueSauvegardee);

langToggle.addEventListener('click', function() {
    const langueActuelle = document.documentElement.lang === 'en' ? 'en' : 'fr';
    appliquerLangue(langueActuelle === 'fr' ? 'en' : 'fr');
});