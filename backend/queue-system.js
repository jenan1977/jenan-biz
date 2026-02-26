/**
 * queue-system.js – In-process priority job queue.
 *
 * Features:
 *  - Priority queue (lower number = higher priority; default 5)
 *  - Configurable concurrency limit (default from config)
 *  - Bounded queue size to prevent memory exhaustion (default 1000)
 *  - Automatic retry with exponential back-off
 *  - Per-job status tracking (pending → running → completed | failed)
 *  - EventEmitter interface for lifecycle events
 */

"use strict";

const { EventEmitter } = require("events");
const { v4: uuidv4 } = require("uuid");
const config = require("./config");
const logger = require("./utils/logger");
const { AppError, ErrorCode } = require("./utils/error-handler");

// ── Job status constants ──────────────────────────────────────────────────────

const JobStatus = Object.freeze({
  PENDING: "pending",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
});

// ── PriorityQueue (min-heap) ──────────────────────────────────────────────────
// Lower `priority` value → processed first (1 = highest, 10 = lowest).

class MinHeap {
  constructor() {
    this._data = [];
  }

  get size() {
    return this._data.length;
  }

  push(item) {
    this._data.push(item);
    this._bubbleUp(this._data.length - 1);
  }

  pop() {
    if (this._data.length === 0) return undefined;
    const top = this._data[0];
    const last = this._data.pop();
    if (this._data.length > 0) {
      this._data[0] = last;
      this._sinkDown(0);
    }
    return top;
  }

  peek() {
    return this._data[0];
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (this._data[parent].priority <= this._data[i].priority) break;
      [this._data[parent], this._data[i]] = [this._data[i], this._data[parent]];
      i = parent;
    }
  }

  _sinkDown(i) {
    const n = this._data.length;
    for (;;) {
      let smallest = i;
      const l = 2 * i + 1;
      const r = 2 * i + 2;
      if (l < n && this._data[l].priority < this._data[smallest].priority) smallest = l;
      if (r < n && this._data[r].priority < this._data[smallest].priority) smallest = r;
      if (smallest === i) break;
      [this._data[smallest], this._data[i]] = [this._data[i], this._data[smallest]];
      i = smallest;
    }
  }
}

// ── QueueSystem ───────────────────────────────────────────────────────────────

/**
 * @typedef {object} JobRecord
 * @property {string}   id          UUID
 * @property {string}   status      One of JobStatus values
 * @property {number}   priority    1–10, lower = higher priority
 * @property {number}   attempts    Times the job has been attempted
 * @property {number}   maxAttempts Maximum allowed attempts
 * @property {unknown}  result      Set when status = completed
 * @property {string}   [error]     Set when status = failed
 * @property {number}   createdAt   Unix ms timestamp
 * @property {number}   [startedAt] Unix ms timestamp
 * @property {number}   [finishedAt] Unix ms timestamp
 */

class QueueSystem extends EventEmitter {
  /**
   * @param {object} [opts]
   * @param {number} [opts.concurrency]   Max parallel jobs (default from config)
   * @param {number} [opts.maxSize]       Max pending queue depth (default from config)
   * @param {number} [opts.maxRetries]    Max retries per job (default from config)
   * @param {number} [opts.retryBaseDelayMs] Base exponential back-off ms (default from config)
   */
  constructor({
    concurrency = config.QUEUE_CONCURRENCY_LIMIT,
    maxSize = config.QUEUE_MAX_SIZE,
    maxRetries = config.QUEUE_MAX_RETRIES,
    retryBaseDelayMs = config.QUEUE_RETRY_BASE_DELAY_MS,
  } = {}) {
    super();
    this._concurrency = concurrency;
    this._maxSize = maxSize;
    this._maxRetries = maxRetries;
    this._retryBaseDelayMs = retryBaseDelayMs;

    this._heap = new MinHeap();
    /** @type {Map<string, JobRecord>} */
    this._jobs = new Map();
    this._running = 0;
  }

  // ── Public interface ────────────────────────────────────────────────────────

  /**
   * Add a job to the queue.
   *
   * @param {function(): Promise<unknown>} fn        Async job handler.
   * @param {object}  [opts]
   * @param {number}  [opts.priority=5]              Job priority (1–10).
   * @param {number}  [opts.maxAttempts]             Override global maxRetries.
   * @param {string}  [opts.id]                      Provide a custom UUID.
   * @returns {string} Job ID.
   * @throws {AppError} QUEUE_FULL if the queue is at capacity.
   */
  enqueue(fn, { priority = 5, maxAttempts, id } = {}) {
    if (this._heap.size >= this._maxSize) {
      throw new AppError(
        `Queue is full (maxSize=${this._maxSize}). Try again later.`,
        503,
        ErrorCode.QUEUE_FULL
      );
    }

    const jobId = id || uuidv4();
    const record = {
      id: jobId,
      status: JobStatus.PENDING,
      priority,
      attempts: 0,
      maxAttempts: maxAttempts ?? this._maxRetries + 1,
      result: undefined,
      error: undefined,
      createdAt: Date.now(),
      startedAt: undefined,
      finishedAt: undefined,
    };

    this._jobs.set(jobId, record);
    this._heap.push({ priority, jobId, fn, attempts: 0 });

    logger.debug("Job enqueued", { jobId, priority, queueDepth: this._heap.size });
    this.emit("enqueued", { jobId });

    // Kick off processing in the next tick to avoid blocking the caller
    setImmediate(() => this._tick());

    return jobId;
  }

  /**
   * Get the current status record for a job.
   *
   * @param {string} jobId
   * @returns {JobRecord | undefined}
   */
  getJob(jobId) {
    return this._jobs.get(jobId);
  }

  /**
   * Returns a plain-object snapshot of all tracked jobs.
   * @returns {JobRecord[]}
   */
  listJobs() {
    return Array.from(this._jobs.values());
  }

  /** Current number of running jobs. */
  get runningCount() {
    return this._running;
  }

  /** Current number of pending jobs waiting in the heap. */
  get pendingCount() {
    return this._heap.size;
  }

  // ── Internal mechanics ──────────────────────────────────────────────────────

  _tick() {
    while (this._running < this._concurrency && this._heap.size > 0) {
      const { jobId, fn, attempts } = this._heap.pop();
      const record = this._jobs.get(jobId);
      if (!record) continue; // Stale reference (should not happen)

      this._running++;
      record.status = JobStatus.RUNNING;
      record.startedAt = Date.now();
      this.emit("started", { jobId });

      this._run(record, fn, attempts);
    }
  }

  async _run(record, fn, attempts) {
    try {
      const result = await fn();
      record.status = JobStatus.COMPLETED;
      record.result = result;
      record.finishedAt = Date.now();
      logger.info("Job completed", { jobId: record.id, durationMs: record.finishedAt - record.startedAt });
      this.emit("completed", { jobId: record.id, result });
    } catch (err) {
      const nextAttempts = attempts + 1;
      record.attempts = nextAttempts;
      record.error = err?.message || String(err);

      if (nextAttempts < record.maxAttempts) {
        // Exponential back-off before re-queuing
        const delayMs = this._retryBaseDelayMs * Math.pow(2, nextAttempts - 1);
        logger.warn("Job failed; retrying", {
          jobId: record.id,
          attempt: nextAttempts,
          maxAttempts: record.maxAttempts,
          retryAfterMs: delayMs,
          error: record.error,
        });
        record.status = JobStatus.PENDING;
        this.emit("retry", { jobId: record.id, attempt: nextAttempts });

        setTimeout(() => {
          if (this._jobs.has(record.id)) {
            this._heap.push({ priority: record.priority, jobId: record.id, fn, attempts: nextAttempts });
            this._tick();
          }
        }, delayMs);
      } else {
        record.status = JobStatus.FAILED;
        record.finishedAt = Date.now();
        logger.error("Job permanently failed", {
          jobId: record.id,
          attempts: nextAttempts,
          error: record.error,
        });
        this.emit("failed", { jobId: record.id, error: record.error });
      }
    } finally {
      this._running--;
      // Process next item(s) in queue
      setImmediate(() => this._tick());
    }
  }
}

// ── Module-level singleton ────────────────────────────────────────────────────

const queue = new QueueSystem();

module.exports = { QueueSystem, queue, JobStatus };
