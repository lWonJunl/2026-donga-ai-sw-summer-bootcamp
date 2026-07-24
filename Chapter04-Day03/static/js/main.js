const root = document.documentElement;
const themeButton = document.querySelector(".theme-toggle");
const savedTheme = localStorage.getItem("theme");

if (savedTheme) root.dataset.theme = savedTheme;

themeButton.addEventListener("click", () => {
  const next = root.dataset.theme === "dark" ? "light" : "dark";
  root.dataset.theme = next;
  localStorage.setItem("theme", next);
});

const menuButton = document.querySelector(".menu-toggle");
const nav = document.querySelector(".desktop-nav");
menuButton.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
});
nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  nav.classList.remove("open");
  menuButton.setAttribute("aria-expanded", "false");
}));

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add("visible");
    entry.target.querySelectorAll("[data-level]").forEach((bar) => {
      bar.style.width = `${bar.dataset.level}%`;
    });
    observer.unobserve(entry.target);
  });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));

const archiveFilters = [...document.querySelectorAll(".archive-filter")];
const archiveItems = [...document.querySelectorAll(".archive-item")];
const archiveResult = document.querySelector(".archive-result");

if (archiveFilters.length && archiveItems.length && archiveResult) {
  archiveFilters.forEach((button) => button.addEventListener("click", () => {
    const selectedCategory = button.dataset.filter;
    let visibleCount = 0;

    archiveFilters.forEach((filterButton) => {
      const isActive = filterButton === button;
      filterButton.classList.toggle("is-active", isActive);
      filterButton.setAttribute("aria-pressed", String(isActive));
    });

    archiveItems.forEach((item) => {
      const isVisible = selectedCategory === "all"
        || item.dataset.filter === selectedCategory;
      item.hidden = !isVisible;
      if (isVisible) visibleCount += 1;
    });

    archiveResult.textContent = `${archiveResult.dataset.prefix}${visibleCount}${archiveResult.dataset.suffix}`;
  }));
}

const backToTop = document.querySelector(".back-to-top");

if (backToTop) {
  backToTop.addEventListener("click", (event) => {
    event.preventDefault();
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });
}
