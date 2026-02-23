"use strict";
/**
 * comments-widget.js - Comments display and submission for blog-detail.html.
 * Depends on: blog-api.js
 */

let _currentArticleId = null;

function initCommentsWidget(articleId) {
  _currentArticleId = articleId;
  _renderCommentForm();
  // Note: comments list is rendered server-side via article.comments in the detail endpoint
}

function _escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function _renderCommentForm() {
  const container = document.getElementById("comment-form-container");
  if (!container) return;

  container.innerHTML = `
    <div class="comment-form">
      <h4>أضف تعليقاً</h4>
      <div class="field-group">
        <label for="comment-name">الاسم *</label>
        <input type="text" id="comment-name" placeholder="اسمك" required>
      </div>
      <div class="field-group">
        <label for="comment-email">البريد الإلكتروني (اختياري)</label>
        <input type="email" id="comment-email" placeholder="example@email.com">
      </div>
      <div class="field-group">
        <label for="comment-content">التعليق *</label>
        <textarea id="comment-content" rows="4" placeholder="اكتب تعليقك هنا..." required></textarea>
      </div>
      <button onclick="submitComment()" class="btn btn-primary">إرسال التعليق</button>
      <p class="comment-note">سيظهر تعليقك بعد مراجعته من الإدارة.</p>
    </div>`;
}

async function submitComment() {
  if (!_currentArticleId) return;

  const author_name = document.getElementById("comment-name").value.trim();
  const author_email = document.getElementById("comment-email").value.trim();
  const content = document.getElementById("comment-content").value.trim();

  if (!author_name) { alert("الاسم مطلوب"); return; }
  if (!content) { alert("التعليق مطلوب"); return; }

  try {
    await blogApi.addComment(_currentArticleId, { author_name, author_email, content });
    document.getElementById("comment-name").value = "";
    document.getElementById("comment-email").value = "";
    document.getElementById("comment-content").value = "";
    alert("شكراً! سيظهر تعليقك بعد المراجعة.");
  } catch (err) {
    alert("خطأ في إرسال التعليق: " + err.message);
  }
}

/**
 * Render a list of approved comments.
 * @param {Array} comments - Array of comment objects.
 */
function renderComments(comments) {
  const el = document.getElementById("comments-list");
  if (!el) return;

  if (!comments || !comments.length) {
    el.innerHTML = '<p class="empty-state">لا توجد تعليقات بعد. كن أول المعلقين!</p>';
    return;
  }

  el.innerHTML = comments
    .filter((c) => c.is_approved)
    .map(
      (c) => `
      <div class="comment-item">
        <div class="comment-header">
          <span class="comment-author">👤 ${_escHtml(c.author_name)}</span>
          <span class="comment-date">${new Date(c.created_at).toLocaleDateString("ar-SA")}</span>
        </div>
        <p class="comment-content">${_escHtml(c.content)}</p>
      </div>`
    )
    .join("");
}
