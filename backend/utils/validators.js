/**
 * validators.js - Input validation helpers for API request payloads.
 */

"use strict";

const { ValidationError } = require("./error-handler");

// ──────────────────────────────────────────────
// Primitive validators
// ──────────────────────────────────────────────

/**
 * Assert that value is a non-empty string.
 *
 * @param {*}      value
 * @param {string} fieldName
 */
function requireString(value, fieldName) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new ValidationError(`"${fieldName}" must be a non-empty string.`);
  }
}

/**
 * Assert that value is a positive integer.
 *
 * @param {*}      value
 * @param {string} fieldName
 */
function requirePositiveInt(value, fieldName) {
  if (!Number.isInteger(value) || value < 1) {
    throw new ValidationError(`"${fieldName}" must be a positive integer.`);
  }
}

/**
 * Assert that value is one of the allowed options.
 *
 * @param {*}        value
 * @param {string[]} options
 * @param {string}   fieldName
 */
function requireOneOf(value, options, fieldName) {
  if (!options.includes(value)) {
    throw new ValidationError(
      `"${fieldName}" must be one of: ${options.join(", ")}.`
    );
  }
}

// ──────────────────────────────────────────────
// Domain-specific validators
// ──────────────────────────────────────────────

/**
 * Validate a generic AI request payload.
 *
 * @param {object} body
 * @returns {object} Sanitised body
 */
function validateAiRequest(body) {
  if (!body || typeof body !== "object") {
    throw new ValidationError("Request body must be a JSON object.");
  }

  const priority = body.priority ?? 5;
  if (!Number.isInteger(priority) || priority < 1 || priority > 10) {
    throw new ValidationError('"priority" must be an integer between 1 and 10.');
  }

  return { ...body, priority };
}

/**
 * Validate a project-analysis request payload.
 *
 * @param {object} body
 * @returns {object} Sanitised body
 */
function validateAnalyzerRequest(body) {
  const sanitised = validateAiRequest(body);
  requireString(sanitised.projectName, "projectName");
  requireString(sanitised.projectDescription, "projectDescription");
  return sanitised;
}

/**
 * Validate a design-studio request payload.
 *
 * @param {object} body
 * @returns {object} Sanitised body
 */
function validateDesignRequest(body) {
  const sanitised = validateAiRequest(body);
  requireString(sanitised.designBrief, "designBrief");
  return sanitised;
}

/**
 * Validate a course-recommendation request payload.
 *
 * @param {object} body
 * @returns {object} Sanitised body
 */
function validateCoursesRequest(body) {
  const sanitised = validateAiRequest(body);
  requireString(sanitised.topic, "topic");
  return sanitised;
}

module.exports = {
  requireString,
  requirePositiveInt,
  requireOneOf,
  validateAiRequest,
  validateAnalyzerRequest,
  validateDesignRequest,
  validateCoursesRequest,
};
