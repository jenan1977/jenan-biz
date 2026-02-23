"use strict";
/**
 * blog-api.js - Client-side API wrapper for the Blog module.
 * Provides a `blogApi` global object for all blog API calls.
 */

(function (global) {
  const BASE_URL = "/api/v1/blog";

  async function _request(method, path, body = null) {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body !== null) options.body = JSON.stringify(body);

    const res = await fetch(BASE_URL + path, options);
    if (res.status === 204) return null;
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    return data;
  }

  const blogApi = {
    // ── Articles ─────────────────────────────────────────────────────────
    listArticles({ page = 1, per_page = 10, status = "published", category = "", tag = "", search = "" } = {}) {
      const params = new URLSearchParams({ page, per_page, status });
      if (category) params.set("category", category);
      if (tag) params.set("tag", tag);
      if (search) params.set("search", search);
      return _request("GET", `/articles?${params}`);
    },

    searchArticles(q, { page = 1, per_page = 10 } = {}) {
      const params = new URLSearchParams({ q, page, per_page });
      return _request("GET", `/articles/search?${params}`);
    },

    getArticle(slug) {
      return _request("GET", `/articles/${encodeURIComponent(slug)}`);
    },

    createArticle(data) {
      return _request("POST", "/articles", data);
    },

    updateArticle(id, data) {
      return _request("PUT", `/articles/${id}`, data);
    },

    deleteArticle(id) {
      return _request("DELETE", `/articles/${id}`);
    },

    addComment(articleId, data) {
      return _request("POST", `/articles/${articleId}/comments`, data);
    },

    // ── Categories ───────────────────────────────────────────────────────
    listCategories() {
      return _request("GET", "/categories");
    },

    createCategory(data) {
      return _request("POST", "/categories", data);
    },

    // ── Tags ─────────────────────────────────────────────────────────────
    listTags() {
      return _request("GET", "/tags");
    },

    createTag(data) {
      return _request("POST", "/tags", data);
    },

    // ── AI Endpoints ─────────────────────────────────────────────────────
    generateArticle(data) {
      return fetch("/api/blog/ai/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then((r) => r.json());
    },

    improveArticle(id, data) {
      return fetch(`/api/blog/ai/improve/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then((r) => r.json());
    },
  };

  global.blogApi = blogApi;
})(window);
