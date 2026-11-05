/**
 * Portfolio Data Configuration
 * Edit your details, projects, skills, and links here!
 */

const portfolioData = {
  personal: {
    name: "Hiren Grover",
    title: "Full-Stack Software Engineer",
    badge: "Available for new opportunities",
    avatar: "https://avatars.githubusercontent.com/u/327120724?v=4",
    tagline: "Engineering clean, scalable web applications & distributed systems with high performance and intuitive UX.",
    bio: "Passionate Full-Stack Engineer specializing in modern JavaScript/TypeScript ecosystems, robust backend microservices, and cloud architectures. I love turning complex architectural problems into elegant, well-tested, and developer-friendly code.",
    location: "Available for Remote & On-site",
    email: "hirengrover.dev@gmail.com",
    resumeUrl: "#", // Link to your PDF resume or Google Drive link
    stats: [
      { label: "Repositories & Projects", value: "10+" },
      { label: "Frontend & Backend", value: "Full Stack" },
      { label: "Code Quality", value: "100% Clean" },
      { label: "Continuous Learning", value: "24/7" }
    ],
    social: {
      github: "https://github.com/Hiren0810",
      linkedin: "https://www.linkedin.com/in/hiren-grover-2856a6449",
      twitter: "https://x.com",
      email: "mailto:hirengrover.dev@gmail.com"
    }
  },

  skills: [
    {
      category: "Frontend Development",
      icon: "layout",
      items: ["React.js", "Next.js", "TypeScript", "Tailwind CSS", "Vue.js", "HTML5 & CSS3", "State Management (Redux/Zustand)"]
    },
    {
      category: "Backend & Systems",
      icon: "server",
      items: ["Node.js", "Express", "Python", "FastAPI", "Go", "RESTful APIs", "GraphQL", "Microservices"]
    },
    {
      category: "Databases & Storage",
      icon: "database",
      items: ["PostgreSQL", "MongoDB", "Redis", "Prisma ORM", "Supabase", "SQL Optimization"]
    },
    {
      category: "DevOps & Cloud",
      icon: "cloud",
      items: ["Docker", "AWS (EC2, S3, Lambda)", "CI/CD Pipelines", "Git & GitHub Actions", "Linux", "Vercel"]
    },
    {
      category: "Tools & Testing",
      icon: "terminal",
      items: ["Jest & Vitest", "Cypress", "Postman", "Figma", "Webpack / Vite", "Agile & Scrum"]
    }
  ],

  projects: [
    {
      id: "cloud-collaboration-suite",
      title: "CloudFlow - Real-Time Collaboration Suite",
      description: "An enterprise-grade workspace with real-time collaborative document editing, team audio rooms, and granular role-based access control.",
      category: "fullstack",
      image: "assets/images/project1.png",
      gradient: "from-blue-600 to-indigo-900",
      tags: ["Next.js", "TypeScript", "Node.js", "WebSockets", "PostgreSQL", "Tailwind CSS"],
      liveUrl: "https://example.com/demo1",
      githubUrl: "https://github.com",
      featured: true
    },
    {
      id: "ai-analytics-dashboard",
      title: "PulseMetrics - AI-Powered Analytics Dashboard",
      description: "High-throughput telemetry and analytics platform with automated insights generation, interactive visualization charts, and custom alerting.",
      category: "fullstack",
      image: "assets/images/project2.png",
      gradient: "from-purple-600 to-violet-950",
      tags: ["React", "Python", "FastAPI", "Redis", "Apache Kafka", "Docker"],
      liveUrl: "https://example.com/demo2",
      githubUrl: "https://github.com",
      featured: true
    },
    {
      id: "ecommerce-microservice-api",
      title: "OmniCart - High-Concurrency Order API",
      description: "Resilient e-commerce backend built with asynchronous event-driven architecture, Stripe integration, idempotency keys, and automated inventory sync.",
      category: "backend",
      image: "assets/images/project3.png",
      gradient: "from-emerald-600 to-teal-950",
      tags: ["Go", "Node.js", "Stripe API", "MongoDB", "Redis", "Docker"],
      liveUrl: "https://example.com/demo3",
      githubUrl: "https://github.com",
      featured: true
    },
    {
      id: "dev-canvas-ui-system",
      title: "Aura UI - Accessible Design System",
      description: "A lightweight, fully accessible component library built with WCAG AAA compliance, custom theming engine, and zero external runtime dependencies.",
      category: "frontend",
      image: "assets/images/project4.png",
      gradient: "from-pink-600 to-rose-950",
      tags: ["TypeScript", "Tailwind CSS", "Storybook", "Accessibility (a11y)"],
      liveUrl: "https://example.com/demo4",
      githubUrl: "https://github.com",
      featured: false
    }
  ],

  experience: [
    {
      role: "Senior Full-Stack Engineer",
      company: "Tech Innovations Inc.",
      period: "2023 - Present",
      description: "Led development of core SaaS features used by 50,000+ active users. Improved API latency by 45% using Redis caching and query indexing."
    },
    {
      role: "Full-Stack Software Engineer",
      company: "Nexus Digital Labs",
      period: "2021 - 2023",
      description: "Architected microservices with Node.js and React. Built automated CI/CD pipelines on GitHub Actions reducing deploy times by 60%."
    },
    {
      role: "Software Engineering Intern",
      company: "Apex Systems",
      period: "2020 - 2021",
      description: "Developed customer-facing dashboard components and integrated RESTful APIs with automated end-to-end testing."
    }
  ]
};

// Expose globally
window.portfolioData = portfolioData;

