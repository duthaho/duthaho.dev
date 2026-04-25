// ── Auto-number lead + archive (index page) ──────
const grid = document.querySelector('.posts-grid');
if (grid) {
  const total = grid.querySelectorAll(':scope > a').length + 1;
  const pad = String(total).padStart(2, '0');
  grid.style.setProperty('--archive-start', total);
  document.querySelectorAll('.lead-numeral, [data-lead-num]')
    .forEach(el => { el.textContent = pad; });
}

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
const readingTimeEl = document.getElementById('reading-time');
if (article && readingTimeEl) {
  const words = article.textContent.trim().split(/\s+/).length;
  const minutes = Math.max(1, Math.round(words / 200));
  readingTimeEl.textContent = minutes + ' phút';
}

// ── Table of Contents (terminal card in sidebar) ─
const tocSidebar = document.getElementById('toc-sidebar');
if (article && tocSidebar) {
  const headings = article.querySelectorAll('h2');
  if (headings.length > 1) {
    // Build terminal card
    const card = document.createElement('div');
    card.className = 'terminal-card';

    const header = document.createElement('div');
    header.className = 'terminal-header';
    header.innerHTML = '<div class="terminal-dots"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span></div><span class="terminal-filename">toc.md</span>';
    card.appendChild(header);

    const body = document.createElement('div');
    body.className = 'terminal-body toc-body';

    const title = document.createElement('div');
    title.className = 'toc-title';
    title.textContent = 'Mục lục';
    body.appendChild(title);

    const list = document.createElement('ul');
    list.className = 'toc-list';

    headings.forEach((h, i) => {
      const id = 'section-' + i;
      h.id = id;

      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.className = 'toc-link';
      li.appendChild(a);
      list.appendChild(li);
    });

    body.appendChild(list);
    card.appendChild(body);
    tocSidebar.appendChild(card);

    // Active section tracking
    const tocLinks = card.querySelectorAll('.toc-link');
    const sectionObs = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          tocLinks.forEach(l => l.classList.remove('active'));
          const active = card.querySelector('a[href="#' + e.target.id + '"]');
          if (active) active.classList.add('active');
        }
      });
    }, { threshold: 0, rootMargin: '-80px 0px -60% 0px' });

    headings.forEach(h => sectionObs.observe(h));
  }
}
