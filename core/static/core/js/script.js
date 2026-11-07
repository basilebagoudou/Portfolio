
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

// ===== MATRICE : « tirer un fil » =====
// Un clic sur une compétence de la matrice met en évidence les projets qui
// l'utilisent (data-tech="Python|pandas|…") et estompe les autres ; un
// second clic, ou Échap, annule le filtre.
const matrice = document.querySelector('.heatmap');
const cartesProjets = document.querySelectorAll('[data-tech]:is(.case, .project-card)');

function filtrerProjets(tech) {
    matrice.classList.toggle('is-filtering', Boolean(tech));
    matrice.querySelectorAll('tbody tr').forEach(function(tr) {
        const choisi = tr.dataset.tech === tech;
        tr.classList.toggle('is-picked', choisi);
        tr.querySelector('.thread-btn').setAttribute('aria-pressed', choisi);
    });
    const trouves = [];
    cartesProjets.forEach(function(carte) {
        const utilise = tech && carte.dataset.tech.split('|').includes(tech);
        carte.classList.toggle('is-lit', Boolean(utilise));
        carte.classList.toggle('is-dimmed', Boolean(tech) && !utilise);
        if (utilise) trouves.push(carte);
    });
    afficherResultat(tech, trouves);
}

// Résumé sous la matrice (les cartes sont plus haut dans la page) :
// « Python → 4 projets : Home Credit, … » avec un lien vers chaque carte.
function afficherResultat(tech, cartes) {
    const zone = matrice.querySelector('.thread-result');
    zone.textContent = '';
    if (!tech) return;
    const langue = document.documentElement.lang === 'en' ? 'en' : 'fr';
    const n = cartes.length;
    const entete = langue === 'en'
        ? tech + ' → ' + n + ' project' + (n > 1 ? 's' : '') + ': '
        : tech + ' → ' + n + ' projet' + (n > 1 ? 's' : '') + ' : ';
    zone.append(entete);
    cartes.forEach(function(carte, i) {
        const titre = carte.querySelector('h3 [data-lang="' + langue + '"]');
        const lien = document.createElement('a');
        lien.href = '#' + carte.id;
        lien.textContent = (titre ? titre.textContent : carte.id).split(' — ')[0];
        if (i) zone.append(', ');
        zone.append(lien);
    });
}

if (matrice) {
    let filtreActif = null;
    matrice.querySelectorAll('.thread-btn').forEach(function(bouton) {
        bouton.addEventListener('click', function() {
            const tech = bouton.closest('tr').dataset.tech;
            filtreActif = filtreActif === tech ? null : tech;
            filtrerProjets(filtreActif);
        });
    });
    boutonsLangue.forEach(function(bouton) {
        bouton.addEventListener('click', function() { filtrerProjets(filtreActif); });
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && filtreActif) {
            filtreActif = null;
            filtrerProjets(null);
        }
    });
}
