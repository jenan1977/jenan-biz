/**
 * api-client.js - Secure OpenAI client built on the official OpenAI Node SDK.
 *
 * Features:
 * - Uses official openai npm package
 * - API key loaded from environment via config
 * - Per-request timeout: 60 seconds
 * - Structured error mapping (TIMEOUT, QUOTA_EXCEEDED, RATE_LIMIT, etc.)
 * - Automatic retry for transient rate-limit errors
 */

'use strict'

const OpenAI = require('openai')
const config = require('./config')

// Initialise the SDK client once (singleton)
const _client = new OpenAI({
  apiKey: config.openai.apiKey,
  timeout: config.openai.timeout,
  maxRetries: 2  // built-in SDK retry for 429 / 5xx
})

/**
 * Error types returned in the `type` field of ApiError.
 */
const ErrorType = {
  TIMEOUT: 'TIMEOUT',
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',
  RATE_LIMIT: 'RATE_LIMIT',
  INVALID_KEY: 'INVALID_KEY',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN: 'UNKNOWN'
}

class ApiError extends Error {
  constructor (message, type) {
    super(message)
    this.name = 'ApiError'
    this.type = type
  }
}

/**
 * Map an OpenAI SDK error to a typed ApiError.
 * @param {Error} err
 * @returns {ApiError}
 */
function _mapError (err) {
  if (err instanceof OpenAI.APIConnectionTimeoutError || err.code === 'ETIMEDOUT') {
    return new ApiError('Request timed out', ErrorType.TIMEOUT)
  }
  if (err instanceof OpenAI.RateLimitError) {
    return new ApiError('Rate limit exceeded – retry later', ErrorType.RATE_LIMIT)
  }
  if (err instanceof OpenAI.AuthenticationError) {
    return new ApiError('Invalid API key', ErrorType.INVALID_KEY)
  }
  if (err instanceof OpenAI.APIError) {
    if (err.status === 429) {
      const msg = (err.message || '').toLowerCase()
      if (msg.includes('quota')) {
        return new ApiError('OpenAI quota exceeded', ErrorType.QUOTA_EXCEEDED)
      }
      return new ApiError('Rate limit exceeded', ErrorType.RATE_LIMIT)
    }
    if (err.status >= 500) {
      return new ApiError('OpenAI server error', ErrorType.SERVER_ERROR)
    }
  }
  return new ApiError(err.message || 'Unknown API error', ErrorType.UNKNOWN)
}

/**
 * Send a chat completion request.
 *
 * @param {object} options
 * @param {string} options.systemPrompt   System prompt content.
 * @param {string} options.userMessage    User message content.
 * @param {number} [options.temperature=0.7]
 * @param {string} [options.model]        Override model from config.
 * @returns {Promise<string>}             The assistant reply text.
 * @throws  {ApiError}                    On failure.
 */
async function chatCompletion ({ systemPrompt, userMessage, temperature = 0.7, model }) {
  try {
    const response = await _client.chat.completions.create({
      model: model || config.openai.model,
      temperature,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage }
      ]
    })
    return response.choices[0].message.content
  } catch (err) {
    throw _mapError(err)
  }
}

module.exports = { chatCompletion, ApiError, ErrorType }
