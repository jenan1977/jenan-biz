/**
 * request-handler.js - Links request types to system prompts and the queue.
 */

const { queue } = require('./queue-system');
const { chatCompletion } = require('./api-client');
const prompts = require('./prompts');

/**
 * Map of supported request types to their prompt keys and default priorities.
 */
const REQUEST_TYPES = {
  analyzer: { promptKey: 'analyzer', defaultPriority: 8 },
  design: { promptKey: 'design', defaultPriority: 7 },
  courses: { promptKey: 'courses', defaultPriority: 6 },
};

/**
 * Enqueue an AI request and return its job ID.
 *
 * @param {string} type       - One of 'analyzer' | 'design' | 'courses'.
 * @param {string} userMessage - The user's message / data as a string.
 * @param {number} [priority]  - Override queue priority.
 * @returns {string}           - The job ID for polling.
 * @throws {Error}             - If the type is unsupported.
 */
function handle(type, userMessage, priority) {
  const typeConfig = REQUEST_TYPES[type];
  if (!typeConfig) {
    throw new Error(`Unsupported request type: '${type}'. Valid types: ${Object.keys(REQUEST_TYPES).join(', ')}`);
  }

  const systemPrompt = prompts[typeConfig.promptKey];
  const effectivePriority = typeof priority === 'number' ? priority : typeConfig.defaultPriority;

  const jobId = queue.enqueue(
    () => chatCompletion(systemPrompt, userMessage),
    { priority: effectivePriority }
  );

  return jobId;
}

/**
 * Get the current status of a job.
 *
 * @param {string} jobId
 * @returns {object|null}
 */
function getJobStatus(jobId) {
  return queue.getJob(jobId);
}

module.exports = { handle, getJobStatus, REQUEST_TYPES };
