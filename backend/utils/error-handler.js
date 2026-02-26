/**
 * error-handler.js – Unified error handling utilities.
 *
 * Provides:
 *  - AppError   – structured application error with HTTP status and code
 *  - errorMiddleware – Express error-handling middleware
 *  - asyncWrap  – wraps async route handlers to forward thrown errors
 */

"use strict";

const logger = require("./logger");

// ── Error codes ──────────────────────────────────────────────────────────────

const ErrorCode = {
  // Generic
  INTERNAL_ERROR: "INTERNAL_ERROR",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  NOT_FOUND: "NOT_FOUND",
  RATE_LIMITED: "RATE_LIMITED",

  // Queue
  QUEUE_FULL: "QUEUE_FULL",
  JOB_NOT_FOUND: "JOB_NOT_FOUND",
  JOB_FAILED: "JOB_FAILED",

  // OpenAI
  OPENAI_ERROR: "OPENAI_ERROR",
  OPENAI_TIMEOUT: "OPENAI_TIMEOUT",
  OPENAI_QUOTA_EXCEEDED: "OPENAI_QUOTA_EXCEEDED",
};

// ── AppError class ───────────────────────────────────────────────────────────

/**
 * Structured application error.
 *
 * @property {number} httpStatus  – HTTP status code sent to the client
 * @property {string} code        – machine-readable error code (see ErrorCode)
 * @property {object} details     – optional additional context
 */
class AppError extends Error {
  /**
   * @param {string} message      Human-readable error message.
   * @param {number} [httpStatus] HTTP status code (default 500).
   * @param {string} [code]       Error code from ErrorCode (default INTERNAL_ERROR).
   * @param {object} [details]    Extra context attached to the error response.
   */
  constructor(
    message,
    httpStatus = 500,
    code = ErrorCode.INTERNAL_ERROR,
    details = {}
  ) {
    super(message);
    this.name = "AppError";
    this.httpStatus = httpStatus;
    this.code = code;
    this.details = details;
    Error.captureStackTrace(this, this.constructor);
  }
}

// ── Express error middleware ─────────────────────────────────────────────────

/**
 * Central Express error-handling middleware.
 * Must be registered **after** all routes: `app.use(errorMiddleware)`.
 *
 * @param {Error}                      err
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} _next  (required 4-arg signature)
 */
function errorMiddleware(err, req, res, _) {
  const isAppError = err instanceof AppError;

  const httpStatus = isAppError ? err.httpStatus : 500;
  const code = isAppError ? err.code : ErrorCode.INTERNAL_ERROR;
  const message = isAppError ? err.message : "An unexpected error occurred.";
  const details = isAppError ? err.details : {};

  // Log server-side errors with full stack; client errors (4xx) at warn level
  if (httpStatus >= 500) {
    logger.error("Unhandled error", { code, message, stack: err.stack, url: req.originalUrl });
  } else {
    logger.warn("Client error", { code, message, url: req.originalUrl });
  }

  res.status(httpStatus).json({
    error: { code, message, details },
  });
}

// ── asyncWrap helper ─────────────────────────────────────────────────────────

/**
 * Wraps an async Express route handler so that rejected promises are forwarded
 * to `next(err)` automatically.
 *
 * @template {import('express').RequestHandler} T
 * @param {T} fn
 * @returns {import('express').RequestHandler}
 */
function asyncWrap(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

module.exports = { AppError, ErrorCode, errorMiddleware, asyncWrap };
