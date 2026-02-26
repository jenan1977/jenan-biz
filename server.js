/**
 * server.js – Express application entry point.
 *
 * Sets up:
 *  - CORS
 *  - JSON body parsing
 *  - Request logging middleware
 *  - All API routes (/api/analyzer, /api/design, /api/courses)
 *  - Global error handler
 */

"use strict";

const express = require("express");
const path = require("path");

const config = require("./backend/config");
const logger = require("./backend/utils/logger");
const { errorMiddleware } = require("./backend/utils/error-handler");

const analyzerRouter = require("./backend/endpoints/analyzer-endpoint");
const designRouter = require("./backend/endpoints/design-endpoint");
const coursesRouter = require("./backend/endpoints/courses-endpoint");

// ── Validate configuration before starting ────────────────────────────────────
try {
  config.validate();
} catch (err) {
  // Use process.stderr directly here – logger may not be fully initialised yet
  process.stderr.write(`[startup] Configuration error: ${err.message}\n`);
  process.exit(1);
}

// ── Create Express app ────────────────────────────────────────────────────────

const app = express();

// ── Middleware ────────────────────────────────────────────────────────────────

// CORS – allow browser-side requests from any origin in development;
// restrict to the same origin in production.
app.use((req, res, next) => {
  const origin =
    config.NODE_ENV === "production" ? undefined : req.headers.origin || "*";
  if (origin) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
  }
  if (req.method === "OPTIONS") {
    return res.sendStatus(204);
  }
  next();
});

// Body parsing
app.use(express.json({ limit: "2mb" }));
app.use(express.urlencoded({ extended: false, limit: "2mb" }));

// HTTP request logging
app.use(logger.requestLogMiddleware);

// Serve static pages from the /pages directory
app.use("/pages", express.static(path.join(__dirname, "pages")));

// ── API Routes ────────────────────────────────────────────────────────────────

app.use("/api/analyzer", analyzerRouter);
app.use("/api/design", designRouter);
app.use("/api/courses", coursesRouter);

// Health check
app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ── 404 handler ───────────────────────────────────────────────────────────────
app.use((_req, res) => {
  res.status(404).json({ error: { code: "NOT_FOUND", message: "Route not found." } });
});

// ── Global error handler ──────────────────────────────────────────────────────
app.use(errorMiddleware);

// ── Start server ──────────────────────────────────────────────────────────────

const server = app.listen(config.PORT, () => {
  logger.info(`Jenan-Biz AI server started`, {
    port: config.PORT,
    env: config.NODE_ENV,
    concurrency: config.QUEUE_CONCURRENCY_LIMIT,
  });
});

// Graceful shutdown
function shutdown(signal) {
  logger.info(`Received ${signal}; shutting down gracefully…`);
  server.close(() => {
    logger.info("HTTP server closed.");
    process.exit(0);
  });
  // Force exit if server doesn't close within 10 s
  setTimeout(() => process.exit(1), 10_000).unref();
}

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

module.exports = app; // exported for testing
