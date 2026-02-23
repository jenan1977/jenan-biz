/**
 * config.js – Centralised configuration loaded from environment variables.
 * All modules import from here instead of reading process.env directly.
 */

"use strict";

require("dotenv").config();

const config = {
  // ── Application ─────────────────────────────────────────────────────────
  NODE_ENV: process.env.NODE_ENV || "development",
  PORT: parseInt(process.env.PORT || "3000", 10),

  // ── OpenAI ──────────────────────────────────────────────────────────────
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || "",
  OPENAI_MODEL: process.env.OPENAI_MODEL || "gpt-4o",
  /** Maximum tokens per completion response. */
  OPENAI_MAX_TOKENS: parseInt(process.env.OPENAI_MAX_TOKENS || "4096", 10),
  /** Milliseconds before a single OpenAI request is aborted. */
  OPENAI_TIMEOUT_MS: parseInt(process.env.OPENAI_TIMEOUT_MS || "60000", 10),

  // ── Queue ────────────────────────────────────────────────────────────────
  /** How many jobs may run simultaneously. */
  QUEUE_CONCURRENCY_LIMIT: parseInt(process.env.QUEUE_CONCURRENCY_LIMIT || "10", 10),
  /** Maximum jobs that can sit in the pending queue at once. */
  QUEUE_MAX_SIZE: parseInt(process.env.QUEUE_MAX_SIZE || "1000", 10),
  /** Maximum retry attempts for a failed job. */
  QUEUE_MAX_RETRIES: parseInt(process.env.QUEUE_MAX_RETRIES || "3", 10),
  /** Base delay (ms) before the first retry; doubles each subsequent attempt. */
  QUEUE_RETRY_BASE_DELAY_MS: parseInt(process.env.QUEUE_RETRY_BASE_DELAY_MS || "1000", 10),

  // ── Logging ──────────────────────────────────────────────────────────────
  LOG_LEVEL: process.env.LOG_LEVEL || "info",
  LOG_DIR: process.env.LOG_DIR || "logs",
};

/**
 * Validate critical settings at start-up.
 * Throws an error if any required variable is missing or invalid.
 */
function validate() {
  if (!config.OPENAI_API_KEY) {
    throw new Error(
      "OPENAI_API_KEY environment variable is required. " +
        "Set it in .env or the process environment."
    );
  }
  if (config.PORT < 1 || config.PORT > 65535) {
    throw new Error("PORT must be a valid TCP port number (1–65535).");
  }
  if (config.QUEUE_CONCURRENCY_LIMIT < 1) {
    throw new Error("QUEUE_CONCURRENCY_LIMIT must be at least 1.");
  }
  if (config.QUEUE_MAX_SIZE < config.QUEUE_CONCURRENCY_LIMIT) {
    throw new Error("QUEUE_MAX_SIZE must be >= QUEUE_CONCURRENCY_LIMIT.");
  }
}

config.validate = validate;

module.exports = config;
