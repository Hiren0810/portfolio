/**
 * Authentic, Human-Crafted Portfolio Configuration
 * Clean data, grounded projects, and realistic engineering context.
 */

const portfolioData = {
  personal: {
    name: "Hiren Grover",
    handle: "hirengrover",
    title: "Software Engineer",
    subtitle: "Systems, Backend & Full-Stack",
    avatar: "https://avatars.githubusercontent.com/u/327120724?v=4",
    status: "Available for new opportunities",
    location: "Remote / India",
    email: "hirengrover.dev@gmail.com",
    github: "https://github.com/Hiren0810",
    linkedin: "https://www.linkedin.com/in/hiren-grover-2856a6449",
    resumeUrl: "#",

    intro: "Hey, I'm Hiren. I'm a software engineer who enjoys building high-throughput backend services, algorithmic tools, and snappy web applications. I care about writing code that is fast, readable, and easy to maintain over time.",
    
    bio: [
      "Most of my work centers around asynchronous architectures, quantitative market analysis, and distributed system fundamentals. I prefer standard libraries and clear invariants over bloated dependency stacks.",
      "When I'm not writing code, I'm usually studying market mechanics, reading engineering postmortems, or testing new ideas in Python and TypeScript."
    ],

    now: {
      building: "Asynchronous multi-market trading engines & quantitative scanners in Python.",
      exploring: "Database storage engines, WAL persistence, and low-latency network protocols.",
      availableFor: "Full-time software engineering roles, high-impact contract work, or interesting open-source collaborations."
    }
  },

  principles: [
    {
      title: "Performance is a feature",
      desc: "Snappy response times and low memory footprints aren't optimizations to leave for later — they are foundational design choices."
    },
    {
      title: "Standard libraries first",
      desc: "Understanding the underlying protocol and language runtime before pulling in a 50MB dependency prevents tech debt before it begins."
    },
    {
      title: "Predictable & debuggable",
      desc: "Clear invariants, explicit error handling, and structured logging beat clever one-liners every day in production."
    }
  ],

  projects: [
    {
      id: "trading-system",
      title: "Multi-Market Algorithmic Trading System & Scanner",
      category: "Systems & Python",
      highlight: "Flagship Project",
      tagline: "High-throughput asynchronous market monitor & execution engine",
      description: "An institutional-grade algorithmic trading engine in Python capable of scanning 50+ concurrent markets (Crypto, Equities, Forex) in under 1.5 seconds. Implements pure-Python vectorized math for technical confluence (EMA ribbon, RSI, MACD, Bollinger Bands, ATR), dynamic ATR risk-adjusted position sizing, and a real-time web command center via Server-Sent Events.",
      bullets: [
        "Concurrent scanning across 50+ pairs using asyncio coroutines with token-bucket rate limiting",
        "Zero external quantitative C-dependencies; pure Python vector math for all technical indicators",
        "Mathematical risk manager: dynamic ATR stops, trailing profit protection, and portfolio drawdown circuit breaker",
        "Paper broker simulator with slippage and taker fee modeling backed by an SQLite audit trail"
      ],
      tags: ["Python 3.9+", "AsyncIO", "Algorithmic Trading", "Risk Engine", "SQLite", "SSE Dashboard"],
      githubUrl: "https://github.com/Hiren0810/portfolio/tree/main/trading_system",
      localPath: "trading_system/README.md"
    },
    {
      id: "distributed-kv-store",
      title: "Fast Distributed Key-Value Store & Cache",
      category: "Backend & Systems",
      highlight: "Systems",
      tagline: "In-memory cache with WAL persistence and sub-millisecond lookups",
      description: "A lightweight, Redis-inspired key-value storage engine engineered with TCP socket connection pooling, O(1) LRU eviction, and write-ahead log (WAL) persistence for crash recovery.",
      bullets: [
        "Custom binary protocol parser with zero-copy buffer slicing",
        "Thread-safe O(1) LRU cache with configurable memory boundaries",
        "Append-only log persistence with automated background compaction"
      ],
      tags: ["Python", "TCP Sockets", "Concurrency", "WAL Persistence", "LRU Cache"],
      githubUrl: "https://github.com/Hiren0810"
    },
    {
      id: "aura-ui-system",
      title: "Aura UI — Minimalist Interaction Kit",
      category: "Frontend & UI",
      highlight: "Frontend",
      tagline: "Keyboard-first accessible UI primitives with zero runtime dependencies",
      description: "A clean, modern component library crafted with pure CSS variables and modern DOM primitives. Designed with a focus on tactile micro-interactions, smooth spring animations, and WCAG accessibility standards.",
      bullets: [
        "Zero bundle runtime overhead; native browser rendering",
        "Full keyboard navigation and ARIA screen reader compliance",
        "Fluid dark/light color tokens with automatic system preference synchronization"
      ],
      tags: ["TypeScript", "Tailwind CSS", "Accessibility (a11y)", "Design Systems"],
      githubUrl: "https://github.com/Hiren0810"
    },
    {
      id: "logpulse-telemetry",
      title: "LogPulse — Real-Time Telemetry Streamer",
      category: "Cloud & Microservices",
      highlight: "DevOps",
      tagline: "Lightweight log aggregator with Server-Sent Events",
      description: "Real-time log streamer and metrics pipeline that ingests distributed service telemetry and pipes structured events to browser dashboards with backpressure regulation.",
      bullets: [
        "Pipes high-frequency event streams via HTTP Server-Sent Events (SSE)",
        "Regex-based log categorization and live threshold alerting",
        "Containerized with Docker for straightforward deployment"
      ],
      tags: ["Node.js", "WebSockets / SSE", "Docker", "Event-Driven", "Linux"],
      githubUrl: "https://github.com/Hiren0810"
    }
  ],

  stack: [
    {
      group: "Languages",
      skills: ["Python (AsyncIO, Type Hints)", "TypeScript", "JavaScript (ESNext)", "SQL", "HTML5 & Modern CSS"]
    },
    {
      group: "Backend & Systems",
      skills: ["AsyncIO Coroutines", "Node.js / Express", "FastAPI", "RESTful API Design", "WebSockets & SSE", "Event-Driven Architecture"]
    },
    {
      group: "Databases & Storage",
      skills: ["PostgreSQL", "SQLite (Audit & Transactions)", "Redis (Caching & Pub/Sub)", "Data Modeling & Indexing"]
    },
    {
      group: "Tools & DevOps",
      skills: ["Git & Conventional Commits", "Docker & Containers", "Linux Shell / Bash", "GitHub Actions CI/CD", "Tailwind CSS"]
    }
  ]
};

window.portfolioData = portfolioData;
