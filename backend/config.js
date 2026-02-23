/**
 * config.js - Centralized configuration from environment variables.
 */

require('dotenv').config();

const config = {
  // Server
  PORT: parseInt(process.env.PORT || '3000', 10),
  HOST: process.env.HOST || '0.0.0.0',
  NODE_ENV: process.env.NODE_ENV || 'development',

  // OpenAI API
  OPENAI_API_KEY: process.env.OPENAI_API_KEY || '',
  OPENAI_MODEL: process.env.OPENAI_MODEL || 'gpt-4o',
  OPENAI_TIMEOUT_MS: parseInt(process.env.OPENAI_TIMEOUT_MS || '120000', 10),
  OPENAI_MAX_TOKENS: parseInt(process.env.OPENAI_MAX_TOKENS || '4096', 10),

  // Queue
  // Queue – set QUEUE_MAX_CONCURRENCY lower in .env to respect OpenAI rate limits
  QUEUE_MAX_CONCURRENCY: parseInt(process.env.QUEUE_MAX_CONCURRENCY || '1000', 10),
  QUEUE_MAX_ATTEMPTS: parseInt(process.env.QUEUE_MAX_ATTEMPTS || '5', 10),
  QUEUE_BASE_DELAY_MS: parseInt(process.env.QUEUE_BASE_DELAY_MS || '1000', 10),

  // App
  APP_NAME: process.env.APP_NAME || 'Jenan-Biz',
  CORS_ORIGIN: process.env.CORS_ORIGIN || '*',
};

/**
 * Validate that required environment variables are set.
 * Throws an error listing any missing required variables.
 */
function validate() {
  const required = ['OPENAI_API_KEY'];
  const missing = required.filter((key) => !config[key]);
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
        'Copy .env.example to .env and fill in the values.'
    );
  }
}

module.exports = { config, validate };
