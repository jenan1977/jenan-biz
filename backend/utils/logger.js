/**
 * logger.js - Lightweight structured logger.
 *
 * Outputs JSON lines to stdout so that log-aggregation tools can
 * consume them easily.  The log level is read from config.
 */

"use strict";

const config = require("../config");

const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };

const currentLevel = LEVELS[config.LOG_LEVEL] ?? LEVELS.info;

/**
 * Write a structured log entry.
 *
 * @param {"debug"|"info"|"warn"|"error"} level
 * @param {string} message
 * @param {object} [meta]
 */
function log(level, message, meta = {}) {
  if ((LEVELS[level] ?? 0) < currentLevel) return;

  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...meta,
  };

  const output = JSON.stringify(entry);
  if (level === "error" || level === "warn") {
    process.stderr.write(output + "\n");
  } else {
    process.stdout.write(output + "\n");
  }
}

module.exports = {
  debug: (msg, meta) => log("debug", msg, meta),
  info: (msg, meta) => log("info", msg, meta),
  warn: (msg, meta) => log("warn", msg, meta),
  error: (msg, meta) => log("error", msg, meta),
};
