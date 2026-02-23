"use strict";
/**
 * blog-routes-register.js - Register Blog AI routes on an Express app.
 *
 * Usage:
 *   const registerBlogRoutes = require('./backend/blog-routes-register');
 *   registerBlogRoutes(app);
 */

const express = require("express");

const aiGenerator = require("./blog-ai/ai-generator");
const aiImprover = require("./blog-ai/ai-improver");
const aiSummarizer = require("./blog-ai/ai-summarizer");
const aiTranslator = require("./blog-ai/ai-translator");

/**
 * Rate limiter middleware (simple in-memory, production should use Redis).
 */
function rateLimit(windowMs, max) {
  const requests = new Map();
  return function (req, res, next) {
    const key = req.ip || "unknown";
    const now = Date.now();
    const windowStart = now - windowMs;
    const timestamps = (requests.get(key) || []).filter((t) => t > windowStart);
    timestamps.push(now);
    requests.set(key, timestamps);
    if (timestamps.length > max) {
      return res.status(429).json({ error: "Too many requests, please slow down." });
    }
    next();
  };
}

const aiRateLimit = rateLimit(60 * 1000, 10); // 10 req/min per IP

/**
 * Register all blog-related Express routes.
 * @param {import('express').Application} app
 */
function registerBlogRoutes(app) {
  const router = express.Router();

  // AI endpoints (rate-limited)
  router.post("/ai/generate", aiRateLimit, aiGenerator.handler);
  router.post("/ai/improve/:id", aiRateLimit, aiImprover.handler);
  router.post("/ai/summarize/:id", aiRateLimit, aiSummarizer.handler);
  router.post("/ai/translate/:id", aiRateLimit, aiTranslator.handler);

  app.use("/api/blog", router);
}

module.exports = registerBlogRoutes;
