# Hiren | Full-Stack Software Engineer Portfolio

A modern, fast, responsive personal developer portfolio website designed with semantic HTML5, Tailwind CSS, and Vanilla JavaScript. Built with zero build dependencies, clean architecture, and instant deployment for GitHub Pages.

---

## ✨ Features

- **⚡ Blazing Fast & Zero-Build**: Runs directly in the browser or on any static host without requiring `npm install` or build steps.
- **🌗 Dark / Light Mode**: Seamless theme switching with automatic system preference detection and `localStorage` persistence.
- **📱 Fully Responsive**: Flawless experience across mobile phones, tablets, and desktop displays.
- **🎨 Glassmorphism & Modern UI**: Subtle glass backgrounds, clean typography (Plus Jakarta Sans & JetBrains Mono), smooth scroll behavior, and Lucide icons.
- **📂 Dynamic Project Showcase**: Interactive category filters (`All`, `Full-Stack`, `Backend & APIs`, `Frontend`) with source code and live demo links.
- **🛠️ Easy Configuration**: All personal info, projects, skills, and experience are decoupled into `assets/js/portfolio-data.js` for instant updates.
- **📬 Interactive Contact Section**: Email quick-copy with toast notification and functional contact form.
- **🚀 1-Click GitHub Pages Deployment**: Fully compatible with native GitHub Pages.

---

## 📁 Project Structure

```text
Portfolio/
├── index.html                  # Main semantic HTML structure
├── assets/
│   ├── css/
│   │   └── style.css           # Custom styling, animations & glassmorphism
│   └── js/
│       ├── portfolio-data.js   # ⚙️ Your customizable data (name, projects, skills)
│       └── main.js             # Theme toggle, filter logic, dynamic rendering
├── .gitignore                  # Clean repository hygiene
└── README.md                   # Documentation
```

---

## 🛠️ How to Customize Your Info

All of your personal information is isolated in **[`assets/js/portfolio-data.js`](assets/js/portfolio-data.js)**:

1. **Personal Details**: Update your name, title, bio, email, and social profiles.
2. **Projects**: Add, edit, or remove projects. You can assign categories (`fullstack`, `backend`, `frontend`), add tech stack tags, and provide GitHub and live preview links.
3. **Skills**: Customize your technical proficiencies by category.
4. **Experience**: Add your career roles, dates, and milestone descriptions.

---

## 🌐 Deploy to GitHub Pages (Free Hosting)

1. Push this repository to your GitHub account (e.g., `https://github.com/<your-username>/portfolio`).
2. Go to your repository **Settings** on GitHub.
3. Click **Pages** in the left sidebar under the "Code and automation" section.
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main` (or `master`) and folder `/ (root)`.
   - Click **Save**.
5. Within 1–2 minutes, your portfolio will be live at:
   `https://<your-username>.github.io/portfolio/`

*(Tip: If you name your repository `<your-username>.github.io`, it will be served directly at `https://<your-username>.github.io`!)*

---

## 📝 Commit Convention

This repository follows [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature or section
- `fix:` Bug fix
- `style:` Visual, CSS, or styling adjustments
- `docs:` Documentation updates
- `refactor:` Code improvements without altering functionality

