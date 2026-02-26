/**
 * request-handler.js – Bridges incoming HTTP requests to the job queue.
 *
 * Responsibilities:
 *  - Accept a job function and enqueue it via QueueSystem
 *  - Return the job ID immediately (202 Accepted) for async workflows
 *  - Provide a pollStatus helper so endpoints can return full job state
 */

"use strict";

const { queue, JobStatus } = require("./queue-system");
const { AppError, ErrorCode } = require("./utils/error-handler");
const logger = require("./utils/logger");

/**
 * Enqueue a job and reply with 202 Accepted + { jobId, status }.
 *
 * @param {import('express').Response} res
 * @param {function(): Promise<unknown>} jobFn   Async function to execute.
 * @param {object}  [opts]
 * @param {number}  [opts.priority=5]            Job priority (1–10).
 * @param {number}  [opts.maxAttempts]           Override queue default.
 * @returns {void}
 */
function dispatchJob(res, jobFn, { priority = 5, maxAttempts } = {}) {
  const jobId = queue.enqueue(jobFn, { priority, maxAttempts });
  logger.info("Job dispatched", { jobId, priority });
  res.status(202).json({ jobId, status: JobStatus.PENDING });
}

/**
 * Look up a job by ID and respond with its current state.
 *
 * @param {import('express').Request}  req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
function pollStatus(req, res, next) {
  const { jobId } = req.params;
  const record = queue.getJob(jobId);

  if (!record) {
    return next(
      new AppError(`Job '${jobId}' not found.`, 404, ErrorCode.JOB_NOT_FOUND)
    );
  }

  // Determine HTTP status: 200 for terminal states, 202 for in-progress
  const httpStatus =
    record.status === JobStatus.COMPLETED || record.status === JobStatus.FAILED
      ? 200
      : 202;

  res.status(httpStatus).json(record);
}

module.exports = { dispatchJob, pollStatus };
