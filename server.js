/**
 * server.js - Main Express server.
 *
 * Serves the static frontend pages and wires up all AI API endpoints.
 * Start with: npm start
 */

require('dotenv').config();

const path = require('path');
const express = require('express');
const cors = require('cors');

const { config, validate } = require('./backend/config');
const analyzerRouter = require('./backend/endpoints/analyzer-endpoint');
const designRouter = require('./backend/endpoints/design-endpoint');
const coursesRouter = require('./backend/endpoints/courses-endpoint');

// ─── Validate config before starting ─────────────────────────────────────────
try {
  validate();
} catch (err) {
  console.error(`[Server] Configuration error: ${err.message}`);
  process.exit(1);
}

// ─── App setup ────────────────────────────────────────────────────────────────
const app = express();

app.use(cors({ origin: config.CORS_ORIGIN }));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// ─── API Routes ───────────────────────────────────────────────────────────────
app.use('/api/analyzer', analyzerRouter);
app.use('/api/design', designRouter);
app.use('/api/courses', coursesRouter);

// ─── Health check ─────────────────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', app: config.APP_NAME, timestamp: new Date().toISOString() });
});

// ─── Static pages ─────────────────────────────────────────────────────────────
// Serve pages/ directory; projects-analyzer.html is the index for /
app.use(express.static(path.join(__dirname, 'pages'), { index: 'projects-analyzer.html' }));

// ─── Global error handler ─────────────────────────────────────────────────────
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error(`[Server] Unhandled error:`, err);
  const status = err.statusCode || err.status || 500;
  res.status(status).json({
    error: err.message || 'Internal server error',
    code: err.code || 'INTERNAL_ERROR',
  });
});

// ─── Start ────────────────────────────────────────────────────────────────────
const server = app.listen(config.PORT, config.HOST, () => {
  console.log(`[Server] ${config.APP_NAME} running at http://${config.HOST}:${config.PORT}`);
  console.log(`[Server] Visit http://localhost:${config.PORT} to open the project analyzer`);
});

// ─── Graceful shutdown ────────────────────────────────────────────────────────
function shutdown(signal) {
  console.log(`[Server] Received ${signal}. Shutting down gracefully...`);
  server.close(() => {
    console.log('[Server] HTTP server closed.');
    process.exit(0);
  });
  // Force exit after 10 s if graceful shutdown hangs
  setTimeout(() => {
    console.error('[Server] Forced exit after timeout.');
    process.exit(1);
  }, 10000).unref();
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

module.exports = app;
