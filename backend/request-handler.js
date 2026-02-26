/**
 * request-handler.js - Central router that maps request types to the
 * appropriate system prompt and enqueues the OpenAI API call.
 *
 * Usage
 * ─────
 *   const requestHandler = require('./request-handler');
 *   const { requestId, result } = await requestHandler.handle({
 *     type: 'analyzer',
 *     userMessage: '...',
 *     priority: 7,
 *   });
 */

"use strict";

const queue = require("./queue-system");
const { chatCompletion } = require("./api-client");
const analyzerPrompt = require("./prompts/analyzer-prompt");
const designPrompt = require("./prompts/design-prompt");
const coursesPrompt = require("./prompts/courses-prompt");
const logger = require("./utils/logger");
const { AppError } = require("./utils/error-handler");

// Map of robot type → system prompt string.
const PROMPTS = {
  analyzer: analyzerPrompt,
  design: designPrompt,
  courses: coursesPrompt,
};

/**
 * Enqueue an AI request and await its result.
 *
 * @param {object} options
 * @param {string} options.type         One of: 'analyzer' | 'design' | 'courses'
 * @param {string} options.userMessage  The user's input for the model.
 * @param {number} [options.priority]   1-10 (default 5).
 * @returns {Promise<{ requestId: string, result: string }>}
 */
async function handle({ type, userMessage, priority = 5 }) {
  const systemPrompt = PROMPTS[type];
  if (!systemPrompt) {
    throw new AppError(`Unknown request type: "${type}"`, 400, "UNKNOWN_TYPE");
  }

  logger.info("Handling AI request", { type, priority });

  const { id: requestId, promise } = queue.enqueue(
    () => chatCompletion({ systemPrompt, userMessage }),
    { priority }
  );

  const result = await promise;
  return { requestId, result };
}

module.exports = { handle };
