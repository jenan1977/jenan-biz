/**
 * server.js - Main Express server entry point.
 *
 * Starts the HTTP server, mounts all AI endpoint routers, and registers
 * global error handling middleware.
 *
 * Usage:
 *   node server.js
 *   npm start
 */

"use strict";

const express = require("express");
const path = require("path");
const config = require("./backend/config");
const logger = require("./backend/utils/logger");
const { errorMiddleware } = require("./backend/utils/error-handler");

// Endpoint routers
const analyzerRouter = require("./backend/endpoints/analyzer-endpoint");
const designRouter = require("./backend/endpoints/design-endpoint");
const coursesRouter = require("./backend/endpoints/courses-endpoint");

// ── Validate configuration at startup ────────────────────────────────────────
try {
  config.validate();
} catch (err) {
  // Missing OPENAI_API_KEY is a warning in development; fatal in production.
  if (config.DEBUG) {
    logger.warn(`Configuration warning: ${err.message}`);
  } else {
    logger.error(`Configuration error: ${err.message}`);
    process.exit(1);
  }
}

// ── Create Express app ────────────────────────────────────────────────────────
const app = express();

// Parse JSON bodies (limit 1 MB)
app.use(express.json({ limit: "1mb" }));

// Serve static files from the project root (HTML pages, CSS, JS)
app.use(express.static(path.join(__dirname)));

// ── API routes ────────────────────────────────────────────────────────────────
app.use("/api/analyze", analyzerRouter);
app.use("/api/design", designRouter);
app.use("/api/courses", coursesRouter);

// Health check
app.get("/api/health", (req, res) => {
  const queue = require("./backend/queue-system");
  res.json({
    status: "ok",
    app: config.APP_NAME,
    queue: queue.stats(),
  });
});

// ── Global error handler ──────────────────────────────────────────────────────
app.use(errorMiddleware);

// ── Start listening ───────────────────────────────────────────────────────────
app.listen(config.PORT, () => {
  logger.info(`${config.APP_NAME} server started`, { port: config.PORT });
});

module.exports = app; // exported for testing
