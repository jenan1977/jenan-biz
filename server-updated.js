"use strict";
/**
 * server-updated.js - Express server with Blog endpoints registered.
 *
 * This file integrates the blog AI routes into the main Express application.
 * The Python/FastAPI backend (backend/app) handles core CRUD at /api/v1/blog.
 * This Node.js layer handles AI-powered endpoints at /api/blog/ai/*.
 *
 * Start with: node server-updated.js
 */

const express = require("express");
const path = require("path");
const registerBlogRoutes = require("./backend/blog-routes-register");

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: true }));

// Security headers
app.use((_req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "SAMEORIGIN");
  res.setHeader("X-XSS-Protection", "1; mode=block");
  next();
});

// ── Static files ──────────────────────────────────────────────────────────────
app.use(express.static(path.join(__dirname)));

// ── Blog AI routes ────────────────────────────────────────────────────────────
registerBlogRoutes(app);

// ── Health check ──────────────────────────────────────────────────────────────
app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "jenan-biz", timestamp: new Date().toISOString() });
});

// ── 404 handler ───────────────────────────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({ error: "Not found" });
});

// ── Error handler ─────────────────────────────────────────────────────────────
app.use((err, _req, res, _next) => {
  console.error("[server] Unhandled error:", err.message);
  res.status(500).json({ error: "Internal server error" });
});

// ── Start ─────────────────────────────────────────────────────────────────────
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`✅ Jenan-Biz server running on http://localhost:${PORT}`);
    console.log(`   Blog AI endpoints: http://localhost:${PORT}/api/blog/ai/`);
  });
}

module.exports = app;
