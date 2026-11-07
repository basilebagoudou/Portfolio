
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
// les visites suivantes. Le sélecteur lui-même est un switch à deux options
// (FR / EN) toujours visibles, l'option active étant surlignée — comme une
// case à cocher à deux états plutôt qu'un simple bouton qui bascule.
const boutonsLangue = document.querySelectorAll('.lang-option');
const CLE_LANGUE = 'langue-portfolio';

function appliquerLangue(langue) {
    // toggleAttribute (et non el.hidden) : fonctionne aussi sur les <tspan>
    // des graphiques SVG, qui n'ont pas de propriété « hidden ».
    document.querySelectorAll('[data-lang]').forEach(function(el) {
        el.toggleAttribute('hidden', el.getAttribute('data-lang') !== langue);
    });
    boutonsLangue.forEach(function(bouton) {
        const estActif = bouton.dataset.langBtn === langue;
        bouton.classList.toggle('active', estActif);
        bouton.setAttribute('aria-pressed', estActif);
    });
    document.documentElement.lang = langue;
    localStorage.setItem(CLE_LANGUE, langue);
}

const langueSauvegardee = localStorage.getItem(CLE_LANGUE) || 'fr';
appliquerLangue(langueSauvegardee);

boutonsLangue.forEach(function(bouton) {
    bouton.addEventListener('click', function() {
        appliquerLangue(bouton.dataset.langBtn);
    });
});
// ===== CHIFFRES CLÉS : compteur animé =====
// Chaque .kpi-value porte la valeur finale dans data-count ; on fait défiler
// le nombre de 0 à cette valeur la première fois que le bandeau est visible,
// avec le séparateur de milliers de la langue affichée.
function formater(n, langue) {
    return Math.round(n).toLocaleString(langue === 'en' ? 'en-US' : 'fr-FR');
}

function animerCompteur(el) {
    const cible = Number(el.dataset.count);
    const spans = el.querySelectorAll('[data-lang]');
    const duree = 1400;
    const debut = performance.now();
    function etape(maintenant) {
        const p = Math.min((maintenant - debut) / duree, 1);
        const valeur = cible * (1 - Math.pow(1 - p, 3));
        spans.forEach(function(span) {
            span.textContent = formater(valeur, span.getAttribute('data-lang'));
        });
        if (p < 1) requestAnimationFrame(etape);
    }
    requestAnimationFrame(etape);
}

const bandeau = document.querySelector('#chiffres');
const mouvementReduit = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (bandeau && !mouvementReduit) {
    const observateurChiffres = new IntersectionObserver(function(entries, obs) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.querySelectorAll('.kpi-value[data-count]').forEach(animerCompteur);
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.4 });
    observateurChiffres.observe(bandeau);
}
