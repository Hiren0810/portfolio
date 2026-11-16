/**
 * Main Client Script - Minimalist & Responsive
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  renderContent();
  setupInteractivity();
  setupKeyboardShortcuts();

  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Set current year
  const yearEl = document.getElementById('current-year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
});

/**
 * Clean Theme Toggle (Light / Dark)
 */
function initTheme() {
  const toggleBtn = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  function toggle() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', toggle);
  }
}

/**
 * Render dynamic portfolio content
 */
function renderContent() {
  const data = window.portfolioData;
  if (!data) return;

  // Render Projects
  const projectsContainer = document.getElementById('projects-list');
  if (projectsContainer && data.projects) {
    projectsContainer.innerHTML = data.projects.map((p, idx) => `
      <article class="project-card group p-6 rounded-2xl border border-zinc-200 dark:border-zinc-800/90 bg-white dark:bg-zinc-900/60 hover:border-zinc-300 dark:hover:border-zinc-700/80 transition shadow-sm">
        <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 mb-2">
          <div class="flex items-center gap-2.5">
            <h3 class="text-lg font-bold text-zinc-900 dark:text-zinc-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition">
              ${p.title}
            </h3>
          </div>
          <span class="text-xs font-mono text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
            ${p.category}
          </span>
        </div>

        <p class="text-xs font-mono text-blue-600 dark:text-blue-400 font-medium mb-3">
          ${p.tagline}
        </p>

        <p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4">
          ${p.description}
        </p>

        ${p.bullets ? `
          <ul class="space-y-1.5 mb-5 pl-4 border-l-2 border-zinc-100 dark:border-zinc-800 text-xs text-zinc-500 dark:text-zinc-400">
            ${p.bullets.map(bullet => `
              <li class="flex items-start gap-2">
                <span class="text-blue-500 select-none">•</span>
                <span>${bullet}</span>
              </li>
            `).join('')}
          </ul>
        ` : ''}

        <div class="flex flex-wrap items-center justify-between gap-4 pt-3 border-t border-zinc-100 dark:border-zinc-800/60">
          <div class="flex flex-wrap gap-1.5">
            ${p.tags.map(t => `
              <span class="px-2 py-0.5 text-[11px] font-mono rounded bg-zinc-100 dark:bg-zinc-800/80 text-zinc-600 dark:text-zinc-400 border border-zinc-200/50 dark:border-zinc-700/50">
                ${t}
              </span>
            `).join('')}
          </div>

          <a href="${p.githubUrl}" target="_blank" rel="noopener noreferrer" 
             class="inline-flex items-center gap-1.5 text-xs font-mono font-medium text-zinc-700 dark:text-zinc-300 hover:text-blue-600 dark:hover:text-blue-400 transition">
            <span>View Source</span>
            <i data-lucide="arrow-up-right" class="w-3.5 h-3.5"></i>
          </a>
        </div>
      </article>
    `).join('');
  }

  // Render Stack Groups
  const stackContainer = document.getElementById('stack-list');
  if (stackContainer && data.stack) {
    stackContainer.innerHTML = data.stack.map(group => `
      <div class="p-5 rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 bg-zinc-50/50 dark:bg-zinc-900/40">
        <h4 class="text-xs font-mono font-bold uppercase tracking-wider text-zinc-900 dark:text-zinc-200 mb-3 flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
          ${group.group}
        </h4>
        <div class="flex flex-wrap gap-2">
          ${group.skills.map(s => `
            <span class="px-2.5 py-1 text-xs font-mono rounded-lg bg-white dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700/80 shadow-2xs">
              ${s}
            </span>
          `).join('')}
        </div>
      </div>
    `).join('');
  }

  // Render Principles
  const principlesContainer = document.getElementById('principles-list');
  if (principlesContainer && data.principles) {
    principlesContainer.innerHTML = data.principles.map(p => `
      <div class="p-5 rounded-2xl border border-zinc-200/80 dark:border-zinc-800/80 bg-white dark:bg-zinc-900/40">
        <h4 class="text-sm font-bold text-zinc-900 dark:text-zinc-100 mb-1.5">
          ${p.title}
        </h4>
        <p class="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
          ${p.desc}
        </p>
      </div>
    `).join('');
  }
}

/**
 * Copy email helper & notifications
 */
function setupInteractivity() {
  const copyBtns = document.querySelectorAll('.copy-email-trigger');
  copyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const email = window.portfolioData?.personal?.email || 'hirengrover.dev@gmail.com';
      navigator.clipboard.writeText(email).then(() => {
        showToast('Copied email to clipboard: ' + email);
      }).catch(() => {
        showToast('Error copying email.');
      });
    });
  });
}

/**
 * Tactile developer keyboard shortcuts
 */
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ignore when typing inside input or textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === 't' || e.key === 'T') {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      if (window.lucide) window.lucide.createIcons();
      showToast(`Switched to ${isDark ? 'Dark' : 'Light'} theme`);
    } else if (e.key === 'c' || e.key === 'C') {
      const email = window.portfolioData?.personal?.email || 'hirengrover.dev@gmail.com';
      navigator.clipboard.writeText(email);
      showToast('Copied email to clipboard!');
    }
  });
}

/**
 * Clean minimal toast notification
 */
function showToast(message) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'toast px-4 py-2.5 rounded-xl shadow-lg border border-zinc-700/60 bg-zinc-900 text-zinc-100 dark:bg-zinc-100 dark:text-zinc-900 dark:border-zinc-300 text-xs font-mono font-medium flex items-center gap-2';
  toast.innerHTML = `
    <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(6px)';
    toast.style.transition = 'all 0.18s ease-in';
    setTimeout(() => toast.remove(), 200);
  }, 2400);
}
