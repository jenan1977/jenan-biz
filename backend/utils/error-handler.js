/**
 * error-handler.js - Centralised error handling utilities.
 *
 * Provides helpers to classify errors, build consistent error
 * response payloads and register an Express error middleware.
 */

"use strict";

const logger = require("./logger");

// ──────────────────────────────────────────────
// Error classes
// ──────────────────────────────────────────────

class AppError extends Error {
  /**
   * @param {string} message   Human-readable description.
   * @param {number} [status]  HTTP status code (default 500).
   * @param {string} [code]    Machine-readable error code.
   */
  constructor(message, status = 500, code = "INTERNAL_ERROR") {
    super(message);
    this.name = "AppError";
    this.status = status;
    this.code = code;
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400, "VALIDATION_ERROR");
    this.name = "ValidationError";
  }
}

class RateLimitError extends AppError {
  constructor(message = "Queue capacity reached. Please try again later.") {
    super(message, 429, "RATE_LIMIT_ERROR");
    this.name = "RateLimitError";
  }
}

class ApiError extends AppError {
  /**
   * @param {string} message
   * @param {number} [status]
   * @param {object} [upstream]  Original upstream error payload.
   */
  constructor(message, status = 502, upstream = null) {
    super(message, status, "API_ERROR");
    this.name = "ApiError";
    this.upstream = upstream;
  }
}

// ──────────────────────────────────────────────
// Response builder
// ──────────────────────────────────────────────

/**
 * Build a normalised error response object.
 *
 * @param {Error} err
 * @returns {{ success: false, error: { code: string, message: string } }}
 */
function buildErrorResponse(err) {
  return {
    success: false,
    error: {
      code: err.code || "INTERNAL_ERROR",
      message: err.message || "An unexpected error occurred.",
    },
  };
}

// ──────────────────────────────────────────────
// Express error middleware
// ──────────────────────────────────────────────

/**
 * Express error-handling middleware.
 * Register with app.use(errorMiddleware) **after** all routes.
 */
function errorMiddleware(err, req, res, _next) {
  const status = err.status || 500;

  logger.error("Request error", {
    path: req.path,
    method: req.method,
    status,
    code: err.code,
    message: err.message,
  });

  res.status(status).json(buildErrorResponse(err));
}

module.exports = {
  AppError,
  ValidationError,
  RateLimitError,
  ApiError,
  buildErrorResponse,
  errorMiddleware,
};
