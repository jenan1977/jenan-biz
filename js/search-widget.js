"use strict";
/**
 * search-widget.js - Search widget for blog pages.
 * Supports live search with debounce.
 */

(function (global) {
  let _searchTimeout = null;

  /**
   * Attach a debounced live search to an input element.
   * @param {string} inputId       - ID of the search input element.
   * @param {Function} onResults   - Callback receiving the search result data.
   * @param {number} [delay=400]   - Debounce delay in ms.
   */
  function attachLiveSearch(inputId, onResults, delay = 400) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener("input", function () {
      clearTimeout(_searchTimeout);
      const q = this.value.trim();
      if (!q) {
        onResults(null);
        return;
      }
      _searchTimeout = setTimeout(async () => {
        try {
          const results = await blogApi.searchArticles(q, { page: 1, per_page: 10 });
          onResults(results);
        } catch (err) {
          console.error("[search-widget] Error:", err.message);
        }
      }, delay);
    });
  }

  /**
   * Render a compact search-results dropdown.
   * @param {string} containerId - ID of the container element.
   * @param {object|null} data   - Paginated results from blogApi or null to clear.
   */
  function renderSearchResults(containerId, data) {
    const el = document.getElementById(containerId);
    if (!el) return;
    if (!data || !data.items.length) { el.innerHTML = ""; el.style.display = "none"; return; }

    el.innerHTML = data.items
      .map(
        (a) =>
          `<a href="blog-detail.html?slug=${encodeURIComponent(a.slug)}" class="search-result-item">
            <span class="result-title">${_escHtml(a.title)}</span>
            <span class="result-meta">${a.category ? _escHtml(a.category.name) : ""}</span>
          </a>`
      )
      .join("");
    el.style.display = "block";
  }

  function _escHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  global.searchWidget = { attachLiveSearch, renderSearchResults };
})(window);
