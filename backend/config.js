require('dotenv').config()

module.exports = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    model: process.env.OPENAI_MODEL || 'gpt-4',
    timeout: 60000
  },
  queue: {
    maxSize: 20000,
    concurrency: 150,
    retryLimit: 3,
    retryDelay: 1000
  },
  server: {
    port: process.env.PORT || 3000,
    host: '0.0.0.0'
  },
  env: process.env.NODE_ENV || 'development'
}

// Validate required env vars
if (!process.env.OPENAI_API_KEY) {
  throw new Error('OPENAI_API_KEY is required')
}
