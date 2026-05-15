
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