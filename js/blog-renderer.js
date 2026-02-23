"use strict";
/**
 * blog-renderer.js - Render blog articles, lists, cards, and pagination.
 * Depends on: blog-api.js
 */

// ── Markdown renderer (minimal, no external dep) ─────────────────────────────
function renderMarkdown(md) {
  if (!md) return "";
  return md
    // Headers
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    // Bold / italic
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    // Code blocks
    .replace(/```[\s\S]*?```/g, (m) => `<pre><code>${escHtml(m.slice(3, -3))}</code></pre>`)
    // Inline code
    .replace(/`(.+?)`/g, "<code>$1</code>")
    // Links
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    // Unordered lists
    .replace(/^- (.+)$/gm, "<li>$1</li>")
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    // Blockquote
    .replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>")
    // Paragraphs (double newlines)
    .replace(/\n\n/g, "</p><p>")
    // Single newlines
    .replace(/\n/g, "<br>");
}

function escHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ── Article Card ─────────────────────────────────────────────────────────────
function renderArticleCard(article) {
  const date = article.published_at
    ? new Date(article.published_at).toLocaleDateString("ar-SA")
    : new Date(article.created_at).toLocaleDateString("ar-SA");
  const cover = article.cover_image
    ? `<img src="${escHtml(article.cover_image)}" alt="${escHtml(article.title)}" class="card-image" loading="lazy">`
    : `<div class="card-image-placeholder">✍️</div>`;
  const tags = (article.tags || [])
    .map((t) => `<span class="tag-chip">${escHtml(t.name)}</span>`)
    .join("");

  return `
    <article class="article-card">
      <a href="blog-detail.html?slug=${escHtml(article.slug)}">
        ${cover}
        <div class="card-body">
          ${article.category ? `<span class="card-category">${escHtml(article.category.name)}</span>` : ""}
          <h3 class="card-title">${escHtml(article.title)}</h3>
          <p class="card-excerpt">${escHtml(article.excerpt || "")}</p>
          <div class="card-meta">
            <span class="card-author">${escHtml(article.author || "Jenan BIZ AI")}</span>
            <span class="card-date">${date}</span>
            <span class="card-views">👁 ${article.views || 0}</span>
          </div>
          <div class="card-tags">${tags}</div>
        </div>
      </a>
    </article>`;
}

// ── Load and render articles grid ────────────────────────────────────────────
async function loadArticles({ page = 1, per_page = 9, status = "published", category = "", search = "" } = {}) {
  try {
    const data = await blogApi.listArticles({ page, per_page, status, category, search });
    const grid = document.getElementById("articles-grid");
    if (!grid) return;

    if (!data.items.length) {
      grid.innerHTML = '<p class="empty-state">لا توجد مقالات حالياً.</p>';
      return;
    }

    grid.innerHTML = data.items.map(renderArticleCard).join("");
    renderPagination("pagination", data, (p) => loadArticles({ page: p, per_page, status, category, search }));
  } catch (err) {
    const grid = document.getElementById("articles-grid");
    if (grid) grid.innerHTML = `<p class="error-state">خطأ في تحميل المقالات: ${escHtml(err.message)}</p>`;
  }
}

// ── Load and render list view ─────────────────────────────────────────────────
async function loadArticlesList({ page = 1, per_page = 10, search = "", category = "" } = {}) {
  try {
    const data = await blogApi.listArticles({ page, per_page, search, category });
    const list = document.getElementById("articles-list");
    if (!list) return;

    if (!data.items.length) {
      list.innerHTML = '<p class="empty-state">لا توجد نتائج.</p>';
      return;
    }

    list.innerHTML = data.items
      .map(
        (a) => `
        <article class="list-article-item">
          <div class="list-article-body">
            ${a.category ? `<span class="card-category">${escHtml(a.category.name)}</span>` : ""}
            <h3><a href="blog-detail.html?slug=${escHtml(a.slug)}">${escHtml(a.title)}</a></h3>
            <p>${escHtml(a.excerpt || "")}</p>
            <div class="card-meta">
              <span>${escHtml(a.author || "Jenan BIZ AI")}</span>
              <span>👁 ${a.views || 0}</span>
              <span>${new Date(a.created_at).toLocaleDateString("ar-SA")}</span>
            </div>
          </div>
          ${a.cover_image ? `<img src="${escHtml(a.cover_image)}" alt="" class="list-article-image" loading="lazy">` : ""}
        </article>`
      )
      .join("");

    renderPagination("pagination", data, (p) => loadArticlesList({ page: p, per_page, search, category }));
  } catch (err) {
    const list = document.getElementById("articles-list");
    if (list) list.innerHTML = `<p class="error-state">خطأ: ${escHtml(err.message)}</p>`;
  }
}

// ── Load single article detail ────────────────────────────────────────────────
async function loadArticleDetail(slug) {
  try {
    const article = await blogApi.getArticle(slug);
    const container = document.getElementById("article-container");
    if (!container) return;

    // Update page meta
    document.title = article.title + " - جنان بيز";
    const metaDesc = document.getElementById("meta-description");
    if (metaDesc) metaDesc.content = article.excerpt || article.title;
    const ogTitle = document.getElementById("og-title");
    if (ogTitle) ogTitle.content = article.title;

    const pubDate = article.published_at
      ? new Date(article.published_at).toLocaleDateString("ar-SA")
      : new Date(article.created_at).toLocaleDateString("ar-SA");

    container.innerHTML = `
      <header class="article-header">
        ${article.cover_image ? `<img src="${escHtml(article.cover_image)}" alt="${escHtml(article.title)}" class="article-cover">` : ""}
        ${article.category ? `<span class="card-category">${escHtml(article.category.name)}</span>` : ""}
        <h1 class="article-title">${escHtml(article.title)}</h1>
        <div class="article-meta">
          <span>✍️ ${escHtml(article.author || "Jenan BIZ AI")}</span>
          <span>📅 ${pubDate}</span>
          <span>👁 ${article.views || 0} مشاهدة</span>
          <span>❤️ ${article.likes || 0} إعجاب</span>
        </div>
      </header>
      <div class="article-body">
        <p>${renderMarkdown(article.content)}</p>
      </div>`;

    // Tags sidebar
    const tagsEl = document.getElementById("article-tags");
    if (tagsEl) {
      tagsEl.innerHTML = (article.tags || [])
        .map((t) => `<a href="blog-list.html?tag=${t.slug}" class="tag-chip">${escHtml(t.name)}</a>`)
        .join("");
    }

    // Schema.org
    const schema = document.getElementById("schema-article");
    if (schema) {
      schema.textContent = JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Article",
        headline: article.title,
        description: article.excerpt || "",
        author: { "@type": "Person", name: article.author },
        datePublished: article.published_at || article.created_at,
        dateModified: article.updated_at,
        image: article.cover_image || "",
      });
    }

    // Load comments
    if (typeof initCommentsWidget === "function") {
      initCommentsWidget(article.id);
    }
  } catch (err) {
    const container = document.getElementById("article-container");
    if (container) container.innerHTML = `<p class="error-state">تعذّر تحميل المقالة: ${escHtml(err.message)}</p>`;
  }
}

// ── Load categories ───────────────────────────────────────────────────────────
async function loadCategories() {
  try {
    const cats = await blogApi.listCategories();
    const chips = document.getElementById("categories-chips");
    if (!chips) return;
    chips.innerHTML =
      `<button class="chip active" data-category="" onclick="filterByCategory(this, '')">الكل</button>` +
      cats
        .map(
          (c) =>
            `<button class="chip" data-category="${c.slug}" onclick="filterByCategory(this, '${c.slug}')">${escHtml(c.name)}</button>`
        )
        .join("");
  } catch (_) {
    // non-fatal
  }
}

async function loadCategoryOptions(selectId) {
  try {
    const cats = await blogApi.listCategories();
    const sel = document.getElementById(selectId);
    if (!sel) return;
    cats.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name;
      sel.appendChild(opt);
    });
  } catch (_) {
    // non-fatal
  }
}

async function loadTags() {
  try {
    const tags = await blogApi.listTags();
    const bar = document.getElementById("tags-bar");
    if (!bar) return;
    bar.innerHTML = tags
      .map((t) => `<a href="?tag=${t.slug}" class="tag-chip">${escHtml(t.name)}</a>`)
      .join("");
  } catch (_) {
    // non-fatal
  }
}

// ── Pagination ────────────────────────────────────────────────────────────────
function renderPagination(containerId, data, onPageChange) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (data.pages <= 1) { el.innerHTML = ""; return; }

  let html = "";
  for (let i = 1; i <= data.pages; i++) {
    const active = i === data.page ? "active" : "";
    html += `<button class="page-btn ${active}" onclick="(${onPageChange.toString()})(${i})">${i}</button>`;
  }
  el.innerHTML = html;
}

// ── Category filter ────────────────────────────────────────────────────────────
function filterByCategory(btn, slug) {
  document.querySelectorAll(".categories-chips .chip").forEach((c) => c.classList.remove("active"));
  btn.classList.add("active");
  loadArticles({ page: 1, category: slug });
}

// ── Share helpers ────────────────────────────────────────────────────────────
function shareArticle(platform) {
  const url = encodeURIComponent(window.location.href);
  const title = encodeURIComponent(document.title);
  if (platform === "twitter") {
    window.open(`https://twitter.com/intent/tweet?url=${url}&text=${title}`, "_blank");
  } else if (platform === "whatsapp") {
    window.open(`https://wa.me/?text=${title}%20${url}`, "_blank");
  }
}

function copyArticleLink() {
  navigator.clipboard.writeText(window.location.href).then(() => alert("تم نسخ الرابط!"));
}

// ── Search ────────────────────────────────────────────────────────────────────
function searchArticles() {
  const q = document.getElementById("hero-search").value.trim();
  if (q) window.location.href = `blog-list.html?search=${encodeURIComponent(q)}`;
}
