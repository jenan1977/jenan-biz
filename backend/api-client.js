/**
 * api-client.js - Safe OpenAI API client wrapper.
 */

const OpenAI = require('openai');
const { config } = require('./config');

let _client = null;

function getClient() {
  if (!_client) {
    _client = new OpenAI({
      apiKey: config.OPENAI_API_KEY,
      timeout: config.OPENAI_TIMEOUT_MS,
    });
  }
  return _client;
}

/**
 * Known error codes returned by chatCompletion.
 */
const ERROR_CODES = {
  AUTH_ERROR: 'AUTH_ERROR',
  RATE_LIMIT: 'RATE_LIMIT',
  TIMEOUT: 'TIMEOUT',
  CONTEXT_LENGTH: 'CONTEXT_LENGTH',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN: 'UNKNOWN',
};

/**
 * Translate an OpenAI SDK error into a known error code.
 * @param {Error} err
 * @returns {{ code: string, message: string }}
 */
function translateError(err) {
  if (err.status === 401 || err.status === 403) {
    return { code: ERROR_CODES.AUTH_ERROR, message: 'Invalid or missing OpenAI API key.' };
  }
  if (err.status === 429) {
    return { code: ERROR_CODES.RATE_LIMIT, message: 'OpenAI rate limit exceeded. Retry later.' };
  }
  if (err.status === 400 && err.message && err.message.includes('context')) {
    return { code: ERROR_CODES.CONTEXT_LENGTH, message: 'Request exceeds context length limit.' };
  }
  if (err.status >= 500) {
    return { code: ERROR_CODES.SERVER_ERROR, message: 'OpenAI server error. Retry later.' };
  }
  if (err.code === 'ETIMEDOUT' || err.code === 'ECONNABORTED' || err.name === 'APIConnectionTimeoutError') {
    return { code: ERROR_CODES.TIMEOUT, message: 'OpenAI request timed out.' };
  }
  return { code: ERROR_CODES.UNKNOWN, message: err.message || 'Unknown error.' };
}

/**
 * Send a chat completion request to OpenAI.
 *
 * @param {string} systemPrompt  - The system role message.
 * @param {string} userMessage   - The user role message.
 * @returns {Promise<string>}    - The assistant reply text.
 * @throws {{ code: string, message: string }} On any API error.
 */
async function chatCompletion(systemPrompt, userMessage) {
  const client = getClient();
  try {
    const response = await client.chat.completions.create({
      model: config.OPENAI_MODEL,
      max_tokens: config.OPENAI_MAX_TOKENS,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
    });
    const choice = response.choices && response.choices[0];
    if (!choice || !choice.message) {
      throw Object.assign(new Error('Empty response from OpenAI'), { code: ERROR_CODES.UNKNOWN });
    }
    return choice.message.content || '';
  } catch (err) {
    if (err.code && Object.values(ERROR_CODES).includes(err.code)) {
      throw err;
    }
    const translated = translateError(err);
    throw Object.assign(new Error(translated.message), { code: translated.code });
  }
}

module.exports = { chatCompletion, ERROR_CODES };
