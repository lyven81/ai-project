/* ========================================
   SARAWAK LAKSA — APP JS
   ======================================== */

// Active nav link on scroll
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

function updateActiveNav() {
  let current = '';
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 100;
    if (window.scrollY >= sectionTop) {
      current = section.getAttribute('id');
    }
  });
  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === '#' + current) {
      link.classList.add('active');
    }
  });
}

// Fade-in on scroll
const fadeEls = document.querySelectorAll(
  '.ingredient-card, .variation-card, .stall-card, .culture-item, .person-card, .recipe-phase'
);

fadeEls.forEach(el => el.classList.add('fade-in'));

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

fadeEls.forEach(el => observer.observe(el));

// Nav scroll handler
window.addEventListener('scroll', updateActiveNav, { passive: true });

// Smooth scroll for hero button
document.querySelector('.hero-btn')?.addEventListener('click', e => {
  e.preventDefault();
  document.querySelector('#what-is-it')?.scrollIntoView({ behavior: 'smooth' });
});

// Nav brand click scrolls to top
document.querySelector('.nav-brand')?.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
