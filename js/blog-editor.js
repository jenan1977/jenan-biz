/**
 * blog-editor.js – Logic for the write-article.html editor page.
 *
 * Handles: tag management, article save/publish, AI generation,
 *          AI improve, and live markdown preview.
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let editingArticleId = null;
let tagList = [];  // Array of { name: string }

// ---------------------------------------------------------------------------
// Initialisation
// ---------------------------------------------------------------------------
(async function init() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (id) {
        editingArticleId = id;
        document.getElementById('editor-title').textContent = 'تعديل مقال';
        try {
            const article = await BlogAPI.getArticle(id);
            fillEditor(article);
        } catch (e) {
            showStatus('❌ تعذّر تحميل المقال: ' + e.message, 'error');
        }
    }

    // Tag input – Enter key adds tag
    document.getElementById('tag-text').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const name = e.target.value.trim();
            if (name && !tagList.find(t => t.name === name)) {
                addTagChip(name);
            }
            e.target.value = '';
        }
    });
})();

// ---------------------------------------------------------------------------
// Tag helpers
// ---------------------------------------------------------------------------
function addTagChip(name) {
    tagList.push({ name });
    const container = document.getElementById('tag-input');
    const chip = document.createElement('span');
    chip.className = 'tag-chip';
    chip.innerHTML = `${name} <button type="button" onclick="removeTag('${name}', this)">×</button>`;
    container.insertBefore(chip, document.getElementById('tag-text'));
}

function removeTag(name, btn) {
    tagList = tagList.filter(t => t.name !== name);
    btn.parentElement.remove();
}

// ---------------------------------------------------------------------------
// Fill editor from existing article
// ---------------------------------------------------------------------------
function fillEditor(article) {
    document.getElementById('article-title').value = article.title || '';
    document.getElementById('article-summary').value = article.summary || '';
    document.getElementById('article-status').value = article.status || 'draft';
    document.getElementById('article-author').value = article.author || '';
    document.getElementById('article-cover').value = article.cover_image_url || '';
    document.getElementById('article-body').value = article.body || '';
    (article.tags || []).forEach(t => addTagChip(t.name));
}

// ---------------------------------------------------------------------------
// Build API payload from form
// ---------------------------------------------------------------------------
async function buildPayload(status) {
    const title = document.getElementById('article-title').value.trim();
    if (!title) { showStatus('⚠️ العنوان مطلوب.', 'error'); return null; }

    // Ensure tags exist in the backend and collect their IDs
    const tagIds = [];
    for (const tag of tagList) {
        try {
            const created = await BlogAPI.createTag({ name: tag.name });
            tagIds.push(created.id);
        } catch (_) {
            // Tag may already exist; fetch from list
            const tags = await BlogAPI.listTags();
            const found = tags.find(t => t.name === tag.name);
            if (found) tagIds.push(found.id);
        }
    }

    return {
        title,
        summary: document.getElementById('article-summary').value.trim() || null,
        body: document.getElementById('article-body').value,
        cover_image_url: document.getElementById('article-cover').value.trim() || null,
        author: document.getElementById('article-author').value.trim() || null,
        status: status || document.getElementById('article-status').value,
        tag_ids: tagIds,
    };
}

// ---------------------------------------------------------------------------
// Save / Publish
// ---------------------------------------------------------------------------
async function saveArticle() {
    const payload = await buildPayload(null);
    if (!payload) return;
    try {
        let article;
        if (editingArticleId) {
            article = await BlogAPI.updateArticle(editingArticleId, payload);
        } else {
            article = await BlogAPI.createArticle(payload);
            editingArticleId = article.id;
            history.replaceState({}, '', '?id=' + article.id);
        }
        showStatus('✅ تم حفظ المقال بنجاح.', 'success');
    } catch (e) {
        showStatus('❌ ' + e.message, 'error');
    }
}

async function publishArticle() {
    const payload = await buildPayload('published');
    if (!payload) return;
    try {
        let article;
        if (editingArticleId) {
            article = await BlogAPI.updateArticle(editingArticleId, payload);
        } else {
            article = await BlogAPI.createArticle(payload);
            editingArticleId = article.id;
            history.replaceState({}, '', '?id=' + article.id);
        }
        showStatus('🚀 تم نشر المقال بنجاح!', 'success');
        document.getElementById('article-status').value = 'published';
    } catch (e) {
        showStatus('❌ ' + e.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Preview
// ---------------------------------------------------------------------------
function togglePreview() {
    const container = document.getElementById('preview-container');
    const visible = container.style.display !== 'none';
    if (!visible) {
        const body = document.getElementById('article-body').value;
        document.getElementById('preview-panel').innerHTML = BlogRenderer.renderMarkdown(body);
    }
    container.style.display = visible ? 'none' : 'block';
}

// ---------------------------------------------------------------------------
// AI: Improve
// ---------------------------------------------------------------------------
async function improveWithAI() {
    if (!editingArticleId) {
        showStatus('⚠️ احفظ المقال أولاً قبل التحسين بالذكاء الاصطناعي.', 'error');
        return;
    }
    const instructions = prompt('أي تحسينات تريد؟ (اختياري)');
    showStatus('⏳ جاري التحسين...', 'success');
    try {
        const data = await BlogAPI.aiImprove(editingArticleId, instructions || null);
        document.getElementById('article-body').value = data.result;
        showStatus('✅ تم تحسين المقال. راجع المحتوى واحفظ عند الرضا.', 'success');
    } catch (e) {
        showStatus('❌ ' + e.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// AI: Generate
// ---------------------------------------------------------------------------
async function generateWithAI() {
    const topic = document.getElementById('ai-topic').value.trim();
    if (!topic) { showStatus('⚠️ أدخل موضوع المقال أولاً.', 'error'); return; }
    const language = document.getElementById('ai-language').value;
    const words = parseInt(document.getElementById('ai-words').value) || 800;

    const resultDiv = document.getElementById('ai-result');
    resultDiv.style.display = 'block';
    resultDiv.textContent = '⏳ جاري توليد المقال...';

    try {
        const article = await BlogAPI.aiGenerate(topic, { language, targetWordCount: words });
        // Fill editor with generated content
        document.getElementById('article-title').value = article.title;
        document.getElementById('article-body').value = article.body;
        editingArticleId = article.id;
        history.replaceState({}, '', '?id=' + article.id);
        resultDiv.textContent = '✅ تم توليد المقال وحفظه كمسودة. يمكنك الآن تعديله ونشره.';
        showStatus('✅ تم توليد المقال وحفظه كمسودة.', 'success');
    } catch (e) {
        resultDiv.textContent = '❌ ' + e.message;
        showStatus('❌ ' + e.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// Status helper
// ---------------------------------------------------------------------------
function showStatus(msg, type) {
    const el = document.getElementById('status-msg');
    el.textContent = msg;
    el.className = 'status-msg ' + type;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 5000);
}
