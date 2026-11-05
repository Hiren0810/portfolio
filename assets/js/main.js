/**
 * Portfolio Main Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Initializer & Toggle
  initTheme();

  // 2. Render Dynamic Data
  renderSkills();
  renderProjects('all');
  renderExperience();

  // 3. Setup Navigation & Interactivity
  setupNavigation();
  setupProjectFilters();
  setupContactForm();
  setupEmailCopy();

  // 4. Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Set current year in footer
  const yearEl = document.getElementById('current-year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
});

/**
 * Dark / Light Theme Manager
 */
function initTheme() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  const themeToggleMobileBtn = document.getElementById('theme-toggle-mobile');

  // Check saved preference or system preference
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }

  function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  if (themeToggleBtn) themeToggleBtn.addEventListener('click', toggleTheme);
  if (themeToggleMobileBtn) themeToggleMobileBtn.addEventListener('click', toggleTheme);
}

/**
 * Mobile Navigation Drawer Toggle
 */
function setupNavigation() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  const navLinks = document.querySelectorAll('.nav-link-mobile');

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });

    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });
  }

  // Active section indicator on scroll
  const sections = document.querySelectorAll('section[id]');
  const desktopLinks = document.querySelectorAll('.nav-link-desktop');

  window.addEventListener('scroll', () => {
    let current = '';
    const scrollY = window.pageYOffset;

    sections.forEach(section => {
      const sectionHeight = section.offsetHeight;
      const sectionTop = section.offsetTop - 120;
      const sectionId = section.getAttribute('id');

      if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
        current = sectionId;
      }
    });

    desktopLinks.forEach(link => {
      link.classList.remove('text-blue-600', 'dark:text-blue-400', 'font-semibold');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('text-blue-600', 'dark:text-blue-400', 'font-semibold');
      }
    });
  });
}

/**
 * Render Skills Grid
 */
function renderSkills() {
  const container = document.getElementById('skills-grid');
  if (!container || !window.portfolioData) return;

  const { skills } = window.portfolioData;

  container.innerHTML = skills.map(group => `
    <div class="glass p-6 rounded-2xl shadow-sm hover:shadow-md transition duration-300">
      <div class="flex items-center gap-3 mb-4">
        <div class="p-2.5 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
          <i data-lucide="${group.icon}" class="w-5 h-5"></i>
        </div>
        <h3 class="font-bold text-lg text-slate-900 dark:text-white">${group.category}</h3>
      </div>
      <div class="flex flex-wrap gap-2">
        ${group.items.map(item => `
          <span class="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700/80 hover:border-blue-500/50 transition">
            ${item}
          </span>
        `).join('')}
      </div>
    </div>
  `).join('');
}

/**
 * Render Project Cards with Filter
 */
function renderProjects(filter = 'all') {
  const container = document.getElementById('projects-grid');
  if (!container || !window.portfolioData) return;

  const { projects } = window.portfolioData;
  const filtered = filter === 'all' 
    ? projects 
    : projects.filter(p => p.category === filter);

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-500 dark:text-slate-400">
        No projects found in this category.
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(project => `
    <article class="glass rounded-2xl overflow-hidden shadow-sm card-hover flex flex-col justify-between border border-slate-200/80 dark:border-slate-800">
      <div>
        <!-- Visual Banner / Header -->
        <div class="h-48 w-full bg-gradient-to-br ${project.gradient} p-6 relative flex flex-col justify-end text-white overflow-hidden group">
          <div class="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition"></div>
          <div class="absolute top-4 right-4 z-10 flex gap-2">
            ${project.featured ? `
              <span class="px-2.5 py-1 text-xs font-semibold rounded-full bg-white/20 backdrop-blur-md text-white border border-white/30">
                Featured
              </span>
            ` : ''}
          </div>
          <div class="relative z-10">
            <span class="text-xs font-mono uppercase tracking-wider text-blue-200">${project.category}</span>
            <h3 class="text-xl font-bold mt-1 text-white leading-tight drop-shadow-sm">${project.title}</h3>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6">
          <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-5">
            ${project.description}
          </p>

          <!-- Tags -->
          <div class="flex flex-wrap gap-1.5 mb-6">
            ${project.tags.map(tag => `
              <span class="px-2.5 py-1 text-xs font-mono rounded-md bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300">
                ${tag}
              </span>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- Links Footer -->
      <div class="px-6 pb-6 pt-2 flex items-center justify-between border-t border-slate-100 dark:border-slate-800/60">
        <a href="${project.githubUrl}" target="_blank" rel="noopener noreferrer" 
           class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition">
          <i data-lucide="github" class="w-4 h-4"></i>
          <span>Source Code</span>
        </a>
        <a href="${project.liveUrl}" target="_blank" rel="noopener noreferrer" 
           class="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition">
          <span>Live Demo</span>
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </a>
      </div>
    </article>
  `).join('');

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

/**
 * Filter Buttons Listener
 */
function setupProjectFilters() {
  const filterBtns = document.querySelectorAll('.project-filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
        b.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      });

      btn.classList.add('bg-blue-600', 'text-white', 'shadow-md');
      btn.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');

      const filter = btn.getAttribute('data-filter') || 'all';
      renderProjects(filter);
    });
  });
}

/**
 * Render Experience Timeline
 */
function renderExperience() {
  const container = document.getElementById('experience-timeline');
  if (!container || !window.portfolioData) return;

  const { experience } = window.portfolioData;

  container.innerHTML = experience.map((item, index) => `
    <div class="relative pl-8 pb-8 ${index === experience.length - 1 ? '' : 'border-l-2 border-slate-200 dark:border-slate-800'}">
      <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-600 ring-4 ring-white dark:ring-slate-900"></div>
      <div class="glass p-5 rounded-xl shadow-sm">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-1">
          <h4 class="font-bold text-base text-slate-900 dark:text-white">${item.role}</h4>
          <span class="text-xs font-mono font-medium px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400">
            ${item.period}
          </span>
        </div>
        <div class="text-sm font-semibold text-slate-600 dark:text-slate-400 mb-2">
          ${item.company}
        </div>
        <p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          ${item.description}
        </p>
      </div>
    </div>
  `).join('');
}

/**
 * Copy Email to Clipboard helper
 */
function setupEmailCopy() {
  const copyBtn = document.getElementById('copy-email-btn');
  if (!copyBtn) return;

  copyBtn.addEventListener('click', () => {
    const email = window.portfolioData?.personal?.email || 'hiren.dev@example.com';
    navigator.clipboard.writeText(email).then(() => {
      showToast('Email address copied to clipboard!', 'success');
    }).catch(() => {
      showToast('Could not copy email.', 'error');
    });
  });
}

/**
 * Contact Form Handler
 */
function setupContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const nameInput = document.getElementById('form-name');
    const emailInput = document.getElementById('form-email');
    const messageInput = document.getElementById('form-message');

    if (!nameInput.value.trim() || !emailInput.value.trim() || !messageInput.value.trim()) {
      showToast('Please fill out all fields.', 'error');
      return;
    }

    // Submit feedback
    showToast('Thank you! Your message has been sent.', 'success');
    form.reset();
  });
}

/**
 * Toast Notification system
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const bgColor = type === 'success' ? 'bg-emerald-600 text-white' : type === 'error' ? 'bg-rose-600 text-white' : 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900';

  toast.className = `toast px-4 py-3 rounded-xl shadow-lg flex items-center gap-3 text-sm font-medium ${bgColor}`;
  toast.innerHTML = `
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.2s ease-in';
    setTimeout(() => toast.remove(), 200);
  }, 3200);
}

