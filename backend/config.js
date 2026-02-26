/**
 * config.js - Centralised application configuration.
 *
 * All runtime settings are read from environment variables so that
 * secrets never appear in source code.  Call loadConfig() once at
 * startup and then import the returned object wherever settings are
 * needed.
 */

"use strict";

const dotenv = require("dotenv");
dotenv.config();

// ──────────────────────────────────────────────
// Queue settings
// ──────────────────────────────────────────────
const QUEUE_CONCURRENCY = parseInt(process.env.QUEUE_CONCURRENCY || "50", 10);
const QUEUE_MAX_SIZE = parseInt(process.env.QUEUE_MAX_SIZE || "1000", 10);
const QUEUE_RETRY_LIMIT = parseInt(process.env.QUEUE_RETRY_LIMIT || "3", 10);
const QUEUE_RETRY_DELAY_MS = parseInt(
  process.env.QUEUE_RETRY_DELAY_MS || "1000",
  10
);

// ──────────────────────────────────────────────
// OpenAI API settings
// ──────────────────────────────────────────────
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || "";
const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-4o";
const OPENAI_TIMEOUT_MS = parseInt(
  process.env.OPENAI_TIMEOUT_MS || "60000",
  10
);

// ──────────────────────────────────────────────
// Application settings
// ──────────────────────────────────────────────
const PORT = parseInt(process.env.PORT || "3000", 10);
const LOG_LEVEL = process.env.LOG_LEVEL || "info";
const APP_NAME = process.env.APP_NAME || "Jenan-Biz";
const DEBUG = process.env.DEBUG === "true" || process.env.NODE_ENV !== "production";

/**
 * Validate that all required settings are present.
 * Throws an Error if any required value is missing.
 */
function validate() {
  if (!OPENAI_API_KEY) {
    throw new Error(
      "OPENAI_API_KEY environment variable is required. " +
        "Copy .env.example to .env and set the key."
    );
  }
  if (QUEUE_CONCURRENCY < 1) {
    throw new Error("QUEUE_CONCURRENCY must be at least 1.");
  }
  if (QUEUE_MAX_SIZE < QUEUE_CONCURRENCY) {
    throw new Error("QUEUE_MAX_SIZE must be >= QUEUE_CONCURRENCY.");
  }
}

module.exports = {
  // Queue
  QUEUE_CONCURRENCY,
  QUEUE_MAX_SIZE,
  QUEUE_RETRY_LIMIT,
  QUEUE_RETRY_DELAY_MS,
  // OpenAI
  OPENAI_API_KEY,
  OPENAI_MODEL,
  OPENAI_TIMEOUT_MS,
  // App
  PORT,
  LOG_LEVEL,
  APP_NAME,
  DEBUG,
  // Helper
  validate,
};
