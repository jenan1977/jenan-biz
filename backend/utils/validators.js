/**
 * validators.js – Input validation utilities.
 *
 * Each validator returns `{ valid: true }` on success or
 * `{ valid: false, errors: string[] }` on failure.
 */

"use strict";

const { AppError, ErrorCode } = require("./error-handler");

// ── Constants ────────────────────────────────────────────────────────────────

const MAX_MESSAGE_LENGTH = 8000;
const MIN_MESSAGE_LENGTH = 1;
const MAX_CONTEXT_FIELDS = 100;

// ── Core validation helpers ──────────────────────────────────────────────────

/**
 * Returns true if `value` is a non-empty string after trimming.
 * @param {unknown} value
 */
function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

/**
 * Returns true if `value` is a plain object (not null, not array).
 * @param {unknown} value
 */
function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

// ── Domain validators ────────────────────────────────────────────────────────

/**
 * Validate an incoming AI chat request body.
 *
 * Expected shape:
 * ```json
 * {
 *   "message": "...",      // required, string, 1–8000 chars
 *   "context": { ... },   // optional, plain object, ≤100 keys
 *   "priority": 1         // optional, integer 1–10
 * }
 * ```
 *
 * @param {unknown} body
 * @returns {{ valid: boolean, errors?: string[] }}
 */
function validateChatRequest(body) {
  const errors = [];

  if (!isPlainObject(body)) {
    return { valid: false, errors: ["Request body must be a JSON object."] };
  }

  // message
  if (!isNonEmptyString(body.message)) {
    errors.push("'message' is required and must be a non-empty string.");
  } else if (body.message.length < MIN_MESSAGE_LENGTH) {
    errors.push(`'message' must be at least ${MIN_MESSAGE_LENGTH} character(s).`);
  } else if (body.message.length > MAX_MESSAGE_LENGTH) {
    errors.push(`'message' must not exceed ${MAX_MESSAGE_LENGTH} characters.`);
  }

  // context (optional)
  if (body.context !== undefined) {
    if (!isPlainObject(body.context)) {
      errors.push("'context' must be a plain object when provided.");
    } else if (Object.keys(body.context).length > MAX_CONTEXT_FIELDS) {
      errors.push(`'context' must not contain more than ${MAX_CONTEXT_FIELDS} keys.`);
    }
  }

  // priority (optional)
  if (body.priority !== undefined) {
    const p = Number(body.priority);
    if (!Number.isInteger(p) || p < 1 || p > 10) {
      errors.push("'priority' must be an integer between 1 and 10.");
    }
  }

  return errors.length === 0 ? { valid: true } : { valid: false, errors };
}

/**
 * Validate a job-status poll request.
 *
 * @param {string} jobId  – must be a non-empty string
 * @returns {{ valid: boolean, errors?: string[] }}
 */
function validateJobId(jobId) {
  if (!isNonEmptyString(jobId)) {
    return { valid: false, errors: ["'jobId' must be a non-empty string."] };
  }
  const uuidPattern =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidPattern.test(jobId)) {
    return { valid: false, errors: ["'jobId' must be a valid UUID v4."] };
  }
  return { valid: true };
}

/**
 * Validate a project-analysis request body.
 *
 * @param {unknown} body
 * @returns {{ valid: boolean, errors?: string[] }}
 */
function validateAnalyzeRequest(body) {
  const base = validateChatRequest(body);
  if (!base.valid) return base;

  const errors = [];

  if (body.projectName !== undefined && !isNonEmptyString(body.projectName)) {
    errors.push("'projectName' must be a non-empty string when provided.");
  }
  if (body.industry !== undefined && !isNonEmptyString(body.industry)) {
    errors.push("'industry' must be a non-empty string when provided.");
  }

  return errors.length === 0 ? { valid: true } : { valid: false, errors };
}

// ── Middleware factory ────────────────────────────────────────────────────────

/**
 * Returns Express middleware that validates the request body using `validatorFn`.
 * Throws an AppError (400) if validation fails.
 *
 * @param {function(unknown): { valid: boolean, errors?: string[] }} validatorFn
 * @returns {import('express').RequestHandler}
 */
function bodyValidator(validatorFn) {
  return (req, _res, next) => {
    const result = validatorFn(req.body);
    if (!result.valid) {
      return next(
        new AppError(
          "Validation failed: " + result.errors.join("; "),
          400,
          ErrorCode.VALIDATION_ERROR,
          { errors: result.errors }
        )
      );
    }
    next();
  };
}

module.exports = {
  validateChatRequest,
  validateJobId,
  validateAnalyzeRequest,
  bodyValidator,
  isNonEmptyString,
  isPlainObject,
};
