/* ===================================================
   CareerAI — main.js
   Global UI interactions: nav, flash messages, animations
   =================================================== */

// ─── Mobile Navigation ─────────────────────────────
function toggleMobileMenu() {
  const menu = document.getElementById("mobileMenu");
  if (menu) menu.classList.toggle("show");
}

// Close mobile menu on outside click
document.addEventListener("click", (e) => {
  const menu = document.getElementById("mobileMenu");
  const toggle = document.querySelector(".nav-toggle");
  if (
    menu &&
    toggle &&
    !menu.contains(e.target) &&
    !toggle.contains(e.target)
  ) {
    menu.classList.remove("show");
  }
});

// ─── Flash Message Auto-Dismiss ────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((flash) => {
    setTimeout(() => {
      flash.style.transition = "opacity 0.4s ease, transform 0.4s ease";
      flash.style.opacity = "0";
      flash.style.transform = "translateX(20px)";
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });
});

// ─── Score Circle Animation ─────────────────────────
// Animates the SVG circle fill on resume result page
function animateScoreCircle() {
  const circle = document.querySelector(".circle-fill");
  if (!circle) return;

  const scoreEl = document.querySelector(".score-circle");
  if (!scoreEl) return;

  const score = parseInt(scoreEl.dataset.score || 0);
  const circumference = 327; // 2 * π * 52
  const targetDash = (score / 100) * circumference;

  // Start from 0
  circle.style.strokeDasharray = `0 ${circumference}`;
  circle.style.transition = "none";

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      circle.style.transition =
        "stroke-dasharray 1.2s cubic-bezier(0.4, 0, 0.2, 1)";
      circle.style.strokeDasharray = `${targetDash} ${circumference}`;
    });
  });
}

// ─── Scroll Reveal Animation ────────────────────────
// Adds 'visible' class to elements with data-reveal as they scroll into view
function initScrollReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  document.querySelectorAll("[data-reveal]").forEach((el) => {
    el.classList.add("reveal-init");
    observer.observe(el);
  });
}

// ─── Staggered Card Animations ──────────────────────
function initCardAnimations() {
  const cards = document.querySelectorAll(
    ".feature-card, .resource-card, .stat-card, .action-btn",
  );
  cards.forEach((card, i) => {
    card.style.animationDelay = `${i * 0.06}s`;
    card.style.animation = "fade-up 0.4s ease both";
  });
}

// ─── Smooth Number Counter ──────────────────────────
function animateCounters() {
  const counters = document.querySelectorAll(".stat-value[data-count]");
  counters.forEach((counter) => {
    const target = parseInt(counter.dataset.count);
    const duration = 1000;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      counter.textContent = Math.floor(current);
    }, 16);
  });
}

// ─── Mini Bar Width Animation ───────────────────────
// Triggers fill animations for analysis bars on resume result page
function animateBars() {
  const bars = document.querySelectorAll(".mini-fill, .bar-fill");
  bars.forEach((bar) => {
    const targetWidth = bar.style.width;
    bar.style.width = "0";
    bar.style.transition = "none";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        bar.style.transition = "width 0.8s cubic-bezier(0.4, 0, 0.2, 1)";
        bar.style.width = targetWidth;
      });
    });
  });
}

// ─── Markdown-like Renderer ─────────────────────────
// Lightweight markdown renderer for chat messages (no external lib)
function renderMarkdown(text) {
  return (
    text
      // Code blocks (``` ```)
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
      // Inline code
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      // Bold **text**
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      // Italic *text*
      .replace(/\*(.+?)\*/g, "<em>$1</em>")
      // Headers ## text
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      // Unordered lists
      .replace(/^- (.+)$/gm, "<li>$1</li>")
      .replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>")
      // Numbered lists
      .replace(/^\d+\. (.+)$/gm, "<li>$1</li>")
      // Checkboxes ✅ ❌
      // Line breaks
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br>")
  );
}

// Apply markdown to all elements with data-markdown attribute
function applyMarkdownRendering() {
  document.querySelectorAll("[data-markdown]").forEach((el) => {
    const raw = el.textContent.trim();
    if (raw) el.innerHTML = renderMarkdown(raw);
  });
}

// ─── Tooltip System ─────────────────────────────────
function initTooltips() {
  document.querySelectorAll("[data-tip]").forEach((el) => {
    el.addEventListener("mouseenter", function () {
      const tip = document.createElement("div");
      tip.className = "tooltip";
      tip.textContent = this.dataset.tip;
      document.body.appendChild(tip);
      const rect = this.getBoundingClientRect();
      tip.style.cssText = `
        position:fixed; background:rgba(15,15,26,0.95); color:#f0f0ff;
        border:1px solid rgba(255,255,255,0.1); border-radius:6px;
        padding:0.4rem 0.7rem; font-size:0.78rem; z-index:9999;
        pointer-events:none; white-space:nowrap;
        top:${rect.top - tip.offsetHeight - 8}px;
        left:${rect.left + rect.width / 2 - tip.offsetWidth / 2}px;
      `;
    });
    el.addEventListener("mouseleave", () => {
      document.querySelectorAll(".tooltip").forEach((t) => t.remove());
    });
  });
}

// ─── DOM Ready ──────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  animateScoreCircle();
  animateBars();
  initScrollReveal();
  initCardAnimations();
  animateCounters();
  applyMarkdownRendering();
  initTooltips();
});

// ─── Safe Mobile Nav Toggle ───────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.querySelector(".nav-toggle");
  const navMobile = document.querySelector(".nav-mobile");

  if (navToggle && navMobile) {
    navToggle.addEventListener("click", () => {
      navMobile.classList.toggle("show");
    });
  }
});
// ─── Export for use in other scripts ───────────────
window.CareerAI = { renderMarkdown, applyMarkdownRendering };
