"use strict";
/**
 * blog-editor.js - Markdown editor helpers for blog-editor.html.
 * Depends on: blog-api.js
 */

let _editorInitialized = false;

function initEditor() {
  if (_editorInitialized) return;
  _editorInitialized = true;

  const textarea = document.getElementById("content-editor");
  const preview = document.getElementById("preview-content");
  if (!textarea || !preview) return;

  // Live preview on input
  textarea.addEventListener("input", function () {
    if (typeof renderMarkdown === "function") {
      preview.innerHTML = renderMarkdown(this.value) || '<p class="preview-placeholder">ابدأ الكتابة لترى المعاينة...</p>';
    }
  });
}

function insertMd(before, after) {
  const ta = document.getElementById("content-editor");
  if (!ta) return;
  const start = ta.selectionStart;
  const end = ta.selectionEnd;
  const selected = ta.value.substring(start, end);
  const replacement = before + selected + after;
  ta.value = ta.value.substring(0, start) + replacement + ta.value.substring(end);
  ta.selectionStart = start + before.length;
  ta.selectionEnd = start + before.length + selected.length;
  ta.focus();
  ta.dispatchEvent(new Event("input"));
}

function togglePreview() {
  const editor = document.querySelector(".editor-panel");
  const preview = document.querySelector(".preview-panel");
  if (!editor || !preview) return;
  editor.classList.toggle("hidden");
  preview.classList.toggle("expanded");
}

// ── Load article for editing ──────────────────────────────────────────────────
async function loadArticleForEdit(id) {
  try {
    // Try to get article by slug or id via search
    const data = await blogApi.listArticles({ page: 1, per_page: 100, status: "" });
    const article = data.items.find((a) => a.id === id);
    if (!article) return;

    document.getElementById("article-id").value = article.id;
    document.getElementById("title").value = article.title || "";
    document.getElementById("status").value = article.status || "draft";
    document.getElementById("author").value = article.author || "";
    document.getElementById("excerpt").value = article.excerpt || "";
    document.getElementById("cover-image").value = article.cover_image || "";

    if (article.category) {
      const sel = document.getElementById("category");
      if (sel) sel.value = article.category.id;
    }
    if (article.tags && article.tags.length) {
      document.getElementById("tags-input").value = article.tags.map((t) => t.name).join(", ");
    }

    const ta = document.getElementById("content-editor");
    if (ta) {
      // Full content is only in the detail endpoint
      const full = await blogApi.getArticle(article.slug);
      ta.value = full.content || "";
      ta.dispatchEvent(new Event("input"));
    }
  } catch (err) {
    console.error("[blog-editor] loadArticleForEdit error:", err.message);
  }
}

// ── Save / Publish ────────────────────────────────────────────────────────────
async function _submitArticle(status) {
  const id = document.getElementById("article-id").value;
  const title = document.getElementById("title").value.trim();
  const content = document.getElementById("content-editor").value.trim();

  if (!title) { alert("العنوان مطلوب"); return; }
  if (!content) { alert("المحتوى مطلوب"); return; }

  const tagsRaw = document.getElementById("tags-input").value;
  const tagNames = tagsRaw
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  const payload = {
    title,
    content,
    status,
    excerpt: document.getElementById("excerpt").value.trim() || null,
    cover_image: document.getElementById("cover-image").value.trim() || null,
    author: document.getElementById("author").value.trim() || "Jenan BIZ AI",
    category_id: document.getElementById("category").value || null,
  };

  try {
    let result;
    if (id) {
      result = await blogApi.updateArticle(id, payload);
      alert("تم تحديث المقالة!");
    } else {
      // Resolve tag IDs first (create tags that don't exist)
      const tag_ids = await resolveTagIds(tagNames);
      result = await blogApi.createArticle({ ...payload, tag_ids });
      document.getElementById("article-id").value = result.id;
      alert("تم إنشاء المقالة!");
    }
    if (status === "published") {
      window.location.href = `blog-detail.html?slug=${result.slug}`;
    }
  } catch (err) {
    alert("خطأ: " + err.message);
  }
}

async function resolveTagIds(names) {
  if (!names.length) return [];
  try {
    const existing = await blogApi.listTags();
    const ids = [];
    for (const name of names) {
      const found = existing.find((t) => t.name.toLowerCase() === name.toLowerCase());
      if (found) {
        ids.push(found.id);
      } else {
        const created = await blogApi.createTag({ name });
        ids.push(created.id);
      }
    }
    return ids;
  } catch (_) {
    return [];
  }
}

function saveDraft() { _submitArticle("draft"); }
function publishArticle() { _submitArticle("published"); }

// ── AI Integration ────────────────────────────────────────────────────────────
function generateWithAI() {
  document.getElementById("ai-modal").style.display = "flex";
}

function closeAIModal() {
  document.getElementById("ai-modal").style.display = "none";
}

async function runAIGenerate() {
  const topic = document.getElementById("ai-topic").value.trim();
  if (!topic) { alert("أدخل موضوع المقالة"); return; }
  const wordCount = parseInt(document.getElementById("ai-word-count").value, 10);

  try {
    closeAIModal();
    const ta = document.getElementById("content-editor");
    ta.value = "⏳ جارٍ التوليد...";

    const result = await blogApi.generateArticle({ topic, wordCount });
    if (result.title) document.getElementById("title").value = result.title;
    if (result.excerpt) document.getElementById("excerpt").value = result.excerpt;
    if (result.content) {
      ta.value = result.content;
      ta.dispatchEvent(new Event("input"));
    }
  } catch (err) {
    alert("خطأ في التوليد: " + err.message);
  }
}

async function improveWithAI() {
  const content = document.getElementById("content-editor").value.trim();
  if (!content) { alert("المحتوى فارغ"); return; }
  const id = document.getElementById("article-id").value;
  try {
    const ta = document.getElementById("content-editor");
    const result = await blogApi.improveArticle(id || "temp", { content, focusAreas: ["grammar", "readability"] });
    if (result.improved_content) {
      ta.value = result.improved_content;
      ta.dispatchEvent(new Event("input"));
      alert("تم تحسين المحتوى: " + (result.changes_summary || ""));
    }
  } catch (err) {
    alert("خطأ في التحسين: " + err.message);
  }
}
