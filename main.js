// ── Reading progress bar ─────────────────────────
const bar = document.getElementById('progress');
if (bar) {
  window.addEventListener('scroll', () => {
    const h = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = h > 0 ? (window.scrollY / h * 100) + '%' : '0%';
  }, { passive: true });
}

// ── Scroll reveal ────────────────────────────────
const obs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal').forEach(el => obs.observe(el));

// ── Reading time ─────────────────────────────────
const article = document.querySelector('.article');
const metaEl = document.querySelector('.hero-meta');
if (article && metaEl) {
  const words = article.textContent.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.round(words / 200));
  const span = document.createElement('span');
  span.textContent = minutes + ' phút đọc';
  metaEl.appendChild(span);
}

// ── Table of Contents ────────────────────────────
if (article) {
  const headings = article.querySelectorAll('h2');
  if (headings.length > 1) {
    // Build ToC element
    const toc = document.createElement('nav');
    toc.className = 'toc';
    toc.setAttribute('aria-label', 'Mục lục');

    const tocTitle = document.createElement('div');
    tocTitle.className = 'toc-title';
    tocTitle.textContent = 'Mục lục';
    toc.appendChild(tocTitle);

    const tocList = document.createElement('ul');
    tocList.className = 'toc-list';

    headings.forEach((h, i) => {
      const id = 'section-' + i;
      h.id = id;

      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.className = 'toc-link';
      li.appendChild(a);
      tocList.appendChild(li);
    });

    toc.appendChild(tocList);
    document.body.appendChild(toc);

    // Active section tracking
    const tocLinks = toc.querySelectorAll('.toc-link');
    const sectionObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          tocLinks.forEach(l => l.classList.remove('active'));
          const id = e.target.id;
          const active = toc.querySelector('a[href="#' + id + '"]');
          if (active) active.classList.add('active');
        }
      });
    }, { threshold: 0, rootMargin: '-80px 0px -60% 0px' });

    headings.forEach(h => sectionObs.observe(h));
  }
}
