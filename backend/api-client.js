/**
 * api-client.js - Secure OpenAI API client.
 *
 * - Reads the API key exclusively from the OPENAI_API_KEY environment
 *   variable; the key is never hard-coded.
 * - Wraps the official `openai` SDK with a thin helper that enforces a
 *   per-request timeout and translates SDK errors into AppError subclasses.
 */

"use strict";

const OpenAI = require("openai");
const config = require("./config");
const logger = require("./utils/logger");
const { ApiError } = require("./utils/error-handler");

// Lazily initialised so the module can be imported before config is fully
// loaded (e.g. in unit tests that override process.env).
let _client = null;

/**
 * Return (and lazily create) the shared OpenAI client instance.
 *
 * @returns {OpenAI}
 */
function getClient() {
  if (!_client) {
    if (!config.OPENAI_API_KEY) {
      throw new ApiError(
        "OPENAI_API_KEY is not set. Cannot create the OpenAI client.",
        500
      );
    }
    _client = new OpenAI({
      apiKey: config.OPENAI_API_KEY,
      timeout: config.OPENAI_TIMEOUT_MS,
    });
  }
  return _client;
}

/**
 * Send a chat-completion request to the OpenAI API.
 *
 * @param {object}   params
 * @param {string}   params.systemPrompt  System-level instructions for the model.
 * @param {string}   params.userMessage   The user's input / question.
 * @param {string}   [params.model]       Overrides the default model from config.
 * @param {number}   [params.maxTokens]   Maximum tokens in the response.
 * @returns {Promise<string>} The assistant's reply text.
 *
 * @throws {ApiError} On any upstream error.
 */
async function chatCompletion({ systemPrompt, userMessage, model, maxTokens }) {
  const client = getClient();
  const usedModel = model || config.OPENAI_MODEL;

  logger.debug("Sending chat completion", { model: usedModel });

  try {
    const response = await client.chat.completions.create({
      model: usedModel,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage },
      ],
      ...(maxTokens ? { max_tokens: maxTokens } : {}),
    });

    const text = response.choices[0]?.message?.content ?? "";
    logger.debug("Chat completion received", {
      model: usedModel,
      promptTokens: response.usage?.prompt_tokens,
      completionTokens: response.usage?.completion_tokens,
    });
    return text;
  } catch (err) {
    // Translate SDK-specific errors into our AppError hierarchy.
    const status = err.status ?? 502;
    const message =
      err.message ?? "Unexpected error communicating with the OpenAI API.";
    logger.error("OpenAI API error", { status, message });
    throw new ApiError(message, status, err);
  }
}

module.exports = { getClient, chatCompletion };
