(function () {
  const STORAGE_KEY = "theme";
  const root = document.documentElement;

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      return null;
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-bs-theme", theme);
    const icon = document.getElementById("theme-icon");
    if (icon) {
      icon.className = theme === "dark" ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
    }
  }

  // Runs immediately (script is loaded in <head>) to avoid a light flash.
  applyTheme(getStoredTheme() || "dark");

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(root.getAttribute("data-bs-theme"));
    const button = document.getElementById("theme-toggle");
    if (!button) {
      return;
    }
    button.addEventListener("click", function () {
      const next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try {
        localStorage.setItem(STORAGE_KEY, next);
      } catch (error) {
        /* storage is unavailable, theme just won't persist */
      }
    });
  });
})();
