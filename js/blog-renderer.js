/**
 * blog-renderer.js – Utility functions for rendering blog content.
 *
 * Provides minimal Markdown → HTML conversion (no external dependencies)
 * and card/detail rendering helpers.
 */

const BlogRenderer = (() => {

    /**
     * Minimal Markdown to HTML converter.
     * Supports: headings, bold, italic, inline code, fenced code blocks,
     *           blockquotes, unordered/ordered lists, paragraphs, and links.
     * XSS-safe: raw HTML is escaped before processing.
     */
    function renderMarkdown(md) {
        if (!md) return '';

        // Escape raw HTML to prevent XSS
        let html = md
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // Fenced code blocks
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
            `<pre><code class="language-${lang}">${code.trimEnd()}</code></pre>`
        );

        // Block-level elements
        const lines = html.split('\n');
        const output = [];
        let inList = null; // 'ul' | 'ol' | null
        let inBlockquote = false;

        const flushList = () => {
            if (inList) { output.push(`</${inList}>`); inList = null; }
        };
        const flushBlockquote = () => {
            if (inBlockquote) { output.push('</blockquote>'); inBlockquote = false; }
        };

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // Skip lines already wrapped in pre (code blocks)
            if (line.startsWith('<pre>') || line.startsWith('</pre>')) {
                flushList(); flushBlockquote();
                output.push(line);
                continue;
            }

            // Headings
            const hMatch = line.match(/^(#{1,6})\s+(.*)/);
            if (hMatch) {
                flushList(); flushBlockquote();
                const level = hMatch[1].length;
                output.push(`<h${level}>${inlineFormat(hMatch[2])}</h${level}>`);
                continue;
            }

            // Blockquote
            if (line.startsWith('&gt; ') || line.startsWith('&gt;')) {
                flushList();
                if (!inBlockquote) { output.push('<blockquote>'); inBlockquote = true; }
                output.push(`<p>${inlineFormat(line.replace(/^&gt;\s?/, ''))}</p>`);
                continue;
            } else {
                flushBlockquote();
            }

            // Unordered list
            const ulMatch = line.match(/^[-*+]\s+(.*)/);
            if (ulMatch) {
                if (inList !== 'ul') { flushList(); output.push('<ul>'); inList = 'ul'; }
                output.push(`<li>${inlineFormat(ulMatch[1])}</li>`);
                continue;
            }

            // Ordered list
            const olMatch = line.match(/^\d+\.\s+(.*)/);
            if (olMatch) {
                if (inList !== 'ol') { flushList(); output.push('<ol>'); inList = 'ol'; }
                output.push(`<li>${inlineFormat(olMatch[1])}</li>`);
                continue;
            }

            flushList();

            // Horizontal rule
            if (/^(---|\*\*\*|___)$/.test(line.trim())) {
                output.push('<hr>');
                continue;
            }

            // Empty line → paragraph break
            if (line.trim() === '') {
                output.push('');
                continue;
            }

            output.push(`<p>${inlineFormat(line)}</p>`);
        }
        flushList();
        flushBlockquote();

        return output.join('\n');
    }

    /** Apply inline Markdown formatting. */
    function inlineFormat(text) {
        return text
            // Bold + italic
            .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
            // Bold
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            // Inline code
            .replace(/`(.+?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    }

    /** Render a short date string. */
    function formatDate(iso) {
        if (!iso) return '';
        return new Date(iso).toLocaleDateString('ar-SA', { year: 'numeric', month: 'long', day: 'numeric' });
    }

    /** Render a single article card (for the list page). */
    function articleCard(article) {
        const coverHtml = article.cover_image_url
            ? `<img class="card-cover" src="${article.cover_image_url}" alt="${article.title}" loading="lazy">`
            : `<div class="card-cover-placeholder">📝</div>`;

        const statusLabel = article.status === 'published' ? 'منشور' : 'مسودة';
        const statusClass = article.status === 'published' ? 'status-published' : 'status-draft';

        const tagsHtml = (article.tags || []).slice(0, 3).map(t =>
            `<span class="badge">${t.name}</span>`).join('');

        const categoryHtml = article.category
            ? `<span class="badge">${article.category.name}</span>` : '';

        const detailUrl = `blog-detail.html?id=${article.id}`;

        return `
<div class="article-card">
    <a href="${detailUrl}">${coverHtml}</a>
    <div class="card-body">
        <div class="card-meta">
            <span class="badge ${statusClass}">${statusLabel}</span>
            ${categoryHtml}
            ${tagsHtml}
        </div>
        <h3 class="card-title"><a href="${detailUrl}">${article.title}</a></h3>
        ${article.summary ? `<p class="card-summary">${article.summary}</p>` : ''}
        <div class="card-footer">
            <span>👤 ${article.author || 'مجهول'}</span>
            <span>👁️ ${article.view_count || 0}</span>
            ${article.read_time_minutes ? `<span>⏱️ ${article.read_time_minutes} دق</span>` : ''}
            <span>📅 ${formatDate(article.created_at)}</span>
        </div>
    </div>
</div>`;
    }

    return { renderMarkdown, inlineFormat, articleCard, formatDate };
})();
