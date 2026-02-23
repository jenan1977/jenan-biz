/**
 * request-handler.js - Central request handler.
 *
 * Wraps the priority queue and the OpenAI API client so individual
 * endpoint routers only have to call handle(type, userData, priority).
 */

'use strict'

const Queue = require('./queue-system')
const apiClient = require('./api-client')
const prompts = require('./prompts')

const queue = new Queue({
  maxSize: 20000,
  concurrency: 150
})

/**
 * Enqueue an AI job and return a promise that resolves when the job completes.
 *
 * @param {string} type      One of 'analyzer' | 'design' | 'courses'.
 * @param {object} userData  Input data passed to the AI.
 * @param {number} [priority=5]  Job priority (1–10, higher = sooner).
 * @returns {Promise<{jobId: string, result: string}>}
 */
function handle (type, userData, priority = 5) {
  return new Promise((resolve, reject) => {
    let jobId

    try {
      jobId = queue.enqueue(async () => {
        const systemPrompt = prompts[type]
        if (!systemPrompt) throw new Error(`Unknown bot type: ${type}`)

        const userMessage = buildUserMessage(type, userData)
        const result = await apiClient.chatCompletion({
          systemPrompt,
          userMessage,
          temperature: 0.7
        })
        return result
      }, priority)
    } catch (err) {
      return reject(err)
    }

    queue.once(`job:${jobId}:complete`, (result) => {
      resolve({ jobId, result })
    })

    queue.once(`job:${jobId}:failed`, (error) => {
      reject(Object.assign(new Error(error.message || String(error)), { jobId }))
    })
  })
}

/**
 * Build a human-readable user message from the request body.
 *
 * @param {string} type
 * @param {object} data
 * @returns {string}
 */
function buildUserMessage (type, data) {
  switch (type) {
    case 'analyzer': {
      const parts = []
      if (data.projectName) parts.push(`اسم المشروع: ${data.projectName}`)
      if (data.description) parts.push(`الوصف: ${data.description}`)
      if (data.budget) parts.push(`الميزانية: ${data.budget} ريال سعودي`)
      if (data.goals) parts.push(`الأهداف: ${data.goals}`)
      return parts.join('\n')
    }
    case 'design': {
      const parts = []
      if (data.brandName) parts.push(`اسم العلامة التجارية: ${data.brandName}`)
      if (data.description) parts.push(`الوصف: ${data.description}`)
      if (data.targetAudience) parts.push(`الجمهور المستهدف: ${data.targetAudience}`)
      return parts.join('\n')
    }
    case 'courses': {
      const parts = []
      if (data.topic) parts.push(`موضوع الدورة: ${data.topic}`)
      if (data.level) parts.push(`المستوى: ${data.level}`)
      if (data.duration) parts.push(`المدة: ${data.duration}`)
      return parts.join('\n')
    }
    default:
      return JSON.stringify(data)
  }
}

module.exports = { handle, queue }
