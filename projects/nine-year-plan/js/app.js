/* ========================================
   NINE YEAR PLAN — APP JS
   ======================================== */

// ── Active nav on scroll ──────────────────
const sections = document.querySelectorAll('section[id], header[id]');
const navLinks  = document.querySelectorAll('.nav-links a');

function updateNav() {
  let current = '';
  sections.forEach(s => {
    if (window.scrollY >= s.offsetTop - 90) current = s.id;
  });
  navLinks.forEach(a => {
    a.classList.remove('active');
    if (a.getAttribute('href') === '#' + current) a.classList.add('active');
  });
}

// ── Fade-in on scroll ─────────────────────
const fadeTargets = document.querySelectorAll(
  '.activity-card, .framework-card, .institution-card, .message-card, ' +
  '.social-card, .stat-card, .timeline-item, .youth-item, .glossary-item, .variation-card'
);
fadeTargets.forEach(el => el.classList.add('fade-in'));

const io = new IntersectionObserver(entries => {
  entries.forEach((e, i) => {
    if (e.isIntersecting) {
      setTimeout(() => e.target.classList.add('visible'), i * 60);
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

fadeTargets.forEach(el => io.observe(el));

// ── Animated number counters ─────────────
function formatNum(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace('.0','') + 'M';
  if (n >= 1000)    return (n / 1000).toFixed(0) + ',000';
  return n.toLocaleString();
}

const statNums = document.querySelectorAll('.stat-num[data-target]');

const counterIO = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el     = entry.target;
    const target = parseInt(el.dataset.target, 10);
    const dur    = 1800;
    const start  = performance.now();

    function tick(now) {
      const p = Math.min((now - start) / dur, 1);
      const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
      el.textContent = formatNum(Math.round(ease * target));
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = formatNum(target);
    }
    requestAnimationFrame(tick);
    counterIO.unobserve(el);
  });
}, { threshold: 0.5 });

statNums.forEach(el => counterIO.observe(el));

// ── Scroll events ─────────────────────────
window.addEventListener('scroll', updateNav, { passive: true });

// ── Hero button ───────────────────────────
document.querySelector('.hero-btn')?.addEventListener('click', e => {
  e.preventDefault();
  document.querySelector('#the-plan')?.scrollIntoView({ behavior: 'smooth' });
});

// ── Nav brand → top ───────────────────────
document.querySelector('.nav-brand')?.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});
