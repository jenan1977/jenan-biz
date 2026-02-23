/**
 * blog-api.js – Client-side wrapper for the Blog API.
 *
 * All methods return Promises.  On non-2xx responses the promise is rejected
 * with an Error whose message contains the server detail string.
 */

const BlogAPI = (() => {
    const BASE_URL = '/api/v1/blog';

    async function _request(method, path, body) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body !== undefined) {
            opts.body = JSON.stringify(body);
        }
        const resp = await fetch(BASE_URL + path, opts);
        if (!resp.ok) {
            let detail = resp.statusText;
            try {
                const data = await resp.json();
                detail = data.detail || JSON.stringify(data);
            } catch (_) { /* ignore */ }
            throw new Error(detail);
        }
        if (resp.status === 204) return null;
        return resp.json();
    }

    // -----------------------------------------------------------------------
    // Categories
    // -----------------------------------------------------------------------
    function listCategories() {
        return _request('GET', '/categories');
    }

    function createCategory(data) {
        return _request('POST', '/categories', data);
    }

    // -----------------------------------------------------------------------
    // Tags
    // -----------------------------------------------------------------------
    function listTags() {
        return _request('GET', '/tags');
    }

    function createTag(data) {
        return _request('POST', '/tags', data);
    }

    // -----------------------------------------------------------------------
    // Articles
    // -----------------------------------------------------------------------
    function listArticles({ search, status, categoryId, tagId, page = 1, pageSize = 20 } = {}) {
        const params = new URLSearchParams();
        if (search) params.set('search', search);
        if (status) params.set('status', status);
        if (categoryId) params.set('category_id', categoryId);
        if (tagId) params.set('tag_id', tagId);
        params.set('page', page);
        params.set('page_size', pageSize);
        return _request('GET', '/articles?' + params.toString());
    }

    function getArticle(idOrSlug) {
        return _request('GET', '/articles/' + encodeURIComponent(idOrSlug));
    }

    function createArticle(data) {
        return _request('POST', '/articles', data);
    }

    function updateArticle(articleId, data) {
        return _request('PATCH', '/articles/' + articleId, data);
    }

    function deleteArticle(articleId) {
        return _request('DELETE', '/articles/' + articleId);
    }

    // -----------------------------------------------------------------------
    // Comments
    // -----------------------------------------------------------------------
    function getComments(articleId) {
        return _request('GET', '/articles/' + articleId + '/comments');
    }

    function addComment(articleId, data) {
        return _request('POST', '/articles/' + articleId + '/comments', data);
    }

    // -----------------------------------------------------------------------
    // Ratings
    // -----------------------------------------------------------------------
    function rateArticle(articleId, data) {
        return _request('POST', '/articles/' + articleId + '/ratings', data);
    }

    function getRatingSummary(articleId) {
        return _request('GET', '/articles/' + articleId + '/ratings/summary');
    }

    // -----------------------------------------------------------------------
    // AI endpoints
    // -----------------------------------------------------------------------
    function aiGenerate(topic, { language = 'ar', targetWordCount = 800, categoryId, tagIds = [] } = {}) {
        return _request('POST', '/articles/auto-generate', {
            topic,
            language,
            target_word_count: targetWordCount,
            category_id: categoryId || null,
            tag_ids: tagIds,
        });
    }

    function aiImprove(articleId, instructions) {
        return _request('POST', '/articles/ai-improve', { article_id: articleId, instructions: instructions || null });
    }

    function aiSummary(articleId, maxSentences = 5) {
        return _request('POST', '/articles/ai-summary', { article_id: articleId, max_sentences: maxSentences });
    }

    function aiTranslate(articleId, targetLanguage) {
        return _request('POST', '/articles/ai-translate', { article_id: articleId, target_language: targetLanguage });
    }

    return {
        listCategories,
        createCategory,
        listTags,
        createTag,
        listArticles,
        getArticle,
        createArticle,
        updateArticle,
        deleteArticle,
        getComments,
        addComment,
        rateArticle,
        getRatingSummary,
        aiGenerate,
        aiImprove,
        aiSummary,
        aiTranslate,
    };
})();
