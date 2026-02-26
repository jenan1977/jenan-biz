/**
 * api-client.js – Secure OpenAI API client.
 *
 * Features:
 *  - API key loaded exclusively from environment variables (never hard-coded)
 *  - Per-request abort timeout
 *  - Structured error mapping to AppError
 *  - Retry on transient network errors (not on quota/auth errors)
 */

"use strict";

const OpenAI = require("openai").default;
const config = require("./config");
const { AppError, ErrorCode } = require("./utils/error-handler");
const logger = require("./utils/logger");

// ── Client singleton ──────────────────────────────────────────────────────────

let _client = null;

/**
 * Returns the shared OpenAI client, creating it on first call.
 * The API key is read from `config.OPENAI_API_KEY` which is backed by the
 * `OPENAI_API_KEY` environment variable – it is never embedded in source code.
 *
 * @returns {OpenAI}
 */
function getClient() {
  if (!_client) {
    if (!config.OPENAI_API_KEY) {
      throw new AppError(
        "OpenAI API key is not configured. Set OPENAI_API_KEY in the environment.",
        500,
        ErrorCode.OPENAI_ERROR
      );
    }
    _client = new OpenAI({
      apiKey: config.OPENAI_API_KEY,
      timeout: config.OPENAI_TIMEOUT_MS,
      maxRetries: 0, // We handle retries in the queue layer
    });
  }
  return _client;
}

// ── Error mapping ─────────────────────────────────────────────────────────────

/**
 * Maps an OpenAI API error to an AppError with the correct HTTP status and code.
 *
 * @param {unknown} err  Raw error thrown by the openai SDK.
 * @returns {AppError}
 */
function mapOpenAIError(err) {
  // OpenAI SDK error types
  if (err && err.constructor) {
    const name = err.constructor.name;
    if (name === "APIConnectionTimeoutError" || name === "APIConnectionError") {
      return new AppError(
        "Request to OpenAI timed out. Please try again.",
        504,
        ErrorCode.OPENAI_TIMEOUT
      );
    }
    if (name === "AuthenticationError") {
      return new AppError(
        "Invalid OpenAI API key. Check OPENAI_API_KEY.",
        500, // 500 because this is a server misconfiguration, not client error
        ErrorCode.OPENAI_ERROR
      );
    }
    if (name === "RateLimitError") {
      return new AppError(
        "OpenAI rate limit reached. Please wait and retry.",
        429,
        ErrorCode.OPENAI_QUOTA_EXCEEDED
      );
    }
  }

  const message = err?.message ?? "Unknown OpenAI error.";
  return new AppError(
    `OpenAI API error: ${message}`,
    502,
    ErrorCode.OPENAI_ERROR
  );
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Send a chat completion request to OpenAI.
 *
 * @param {object}   options
 * @param {string}   options.systemPrompt   System-role content.
 * @param {string}   options.userMessage    User-role content.
 * @param {string}   [options.model]        Model override (default from config).
 * @param {number}   [options.maxTokens]    Max tokens override (default from config).
 * @param {number}   [options.temperature]  Sampling temperature (default 0.7).
 * @returns {Promise<string>}  The assistant's reply text.
 */
async function chatCompletion({ systemPrompt, userMessage, model, maxTokens, temperature = 0.7 }) {
  const client = getClient();
  const requestModel = model || config.OPENAI_MODEL;
  const requestMaxTokens = maxTokens || config.OPENAI_MAX_TOKENS;

  const startMs = Date.now();
  try {
    const response = await client.chat.completions.create({
      model: requestModel,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
      max_tokens: requestMaxTokens,
      temperature,
    });

    const durationMs = Date.now() - startMs;
    const reply = response.choices[0]?.message?.content || "";

    logger.debug("OpenAI chat completion succeeded", {
      model: requestModel,
      promptTokens: response.usage?.prompt_tokens,
      completionTokens: response.usage?.completion_tokens,
      durationMs,
    });

    return reply;
  } catch (err) {
    const durationMs = Date.now() - startMs;
    logger.error("OpenAI chat completion failed", {
      model: requestModel,
      durationMs,
      error: err?.message,
    });
    throw mapOpenAIError(err);
  }
}

module.exports = { chatCompletion, getClient };
