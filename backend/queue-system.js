/**
 * queue-system.js - Priority queue that processes AI requests concurrently.
 *
 * Features
 * ────────
 * - Accepts up to QUEUE_MAX_SIZE (default 1 000) pending jobs.
 * - Runs up to QUEUE_CONCURRENCY (default 50) jobs simultaneously.
 * - Supports numeric priorities 1-10 (higher number → higher priority).
 * - Automatic retry with exponential back-off up to QUEUE_RETRY_LIMIT.
 * - Per-job status tracking: pending | processing | completed | failed.
 * - EventEmitter API so callers can await `job.promise` or subscribe to
 *   'completed' / 'failed' events.
 */

"use strict";

const { EventEmitter } = require("events");
const crypto = require("crypto");
const config = require("./config");
const logger = require("./utils/logger");
const { RateLimitError } = require("./utils/error-handler");

// ──────────────────────────────────────────────
// Job status constants
// ──────────────────────────────────────────────
const STATUS = Object.freeze({
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
});

// ──────────────────────────────────────────────
// QueueSystem
// ──────────────────────────────────────────────

class QueueSystem extends EventEmitter {
  constructor() {
    super();
    /** @type {Map<string, Job>} */
    this._jobs = new Map();
    /** @type {Job[]} Sorted heap (highest priority first). */
    this._heap = [];
    this._active = 0;
  }

  // ── Public API ───────────────────────────────

  /**
   * Add a job to the queue.
   *
   * @param {Function} task        Async function to execute.
   * @param {object}   [options]
   * @param {number}   [options.priority=5]  1-10, higher runs first.
   * @param {string}   [options.requestId]   Custom ID (auto-generated if omitted).
   * @returns {{ id: string, promise: Promise<any>, status: () => string }}
   */
  enqueue(task, { priority = 5, requestId } = {}) {
    if (this._heap.length >= config.QUEUE_MAX_SIZE) {
      throw new RateLimitError();
    }

    const id = requestId || crypto.randomUUID();

    let resolve, reject;
    const promise = new Promise((res, rej) => {
      resolve = res;
      reject = rej;
    });

    const job = {
      id,
      task,
      priority: Math.min(10, Math.max(1, priority)),
      retries: 0,
      status: STATUS.PENDING,
      createdAt: Date.now(),
      resolve,
      reject,
      promise,
    };

    this._jobs.set(id, job);
    this._heapPush(job);

    logger.debug("Job enqueued", { id, priority: job.priority, queueLength: this._heap.length });

    this._tick();

    return {
      id,
      promise,
      status: () => this._jobs.get(id)?.status ?? STATUS.FAILED,
    };
  }

  /** Return a snapshot of queue stats. */
  stats() {
    return {
      pending: this._heap.length,
      active: this._active,
      total: this._jobs.size,
    };
  }

  // ── Internal ─────────────────────────────────

  _tick() {
    while (
      this._active < config.QUEUE_CONCURRENCY &&
      this._heap.length > 0
    ) {
      const job = this._heapPop();
      if (!job) break;
      this._run(job);
    }
  }

  async _run(job) {
    this._active++;
    job.status = STATUS.PROCESSING;

    logger.debug("Job started", { id: job.id, attempt: job.retries + 1 });

    try {
      const result = await job.task();
      job.status = STATUS.COMPLETED;
      logger.info("Job completed", { id: job.id });
      this.emit("completed", { id: job.id, result });
      job.resolve(result);
    } catch (err) {
      if (job.retries < config.QUEUE_RETRY_LIMIT) {
        job.retries++;
        job.status = STATUS.PENDING;
        const delay = config.QUEUE_RETRY_DELAY_MS * Math.pow(2, job.retries - 1);
        logger.warn("Job failed, will retry", {
          id: job.id,
          attempt: job.retries,
          delayMs: delay,
          error: err.message,
        });
        setTimeout(() => {
          this._heapPush(job);
          this._tick();
        }, delay);
      } else {
        job.status = STATUS.FAILED;
        logger.error("Job permanently failed", {
          id: job.id,
          attempts: job.retries + 1,
          error: err.message,
        });
        this.emit("failed", { id: job.id, error: err });
        job.reject(err);
      }
    } finally {
      this._active--;
      this._tick();
    }
  }

  // ── Min-max heap (max by priority) ───────────

  _heapPush(job) {
    this._heap.push(job);
    this._bubbleUp(this._heap.length - 1);
  }

  _heapPop() {
    if (this._heap.length === 0) return null;
    const top = this._heap[0];
    const last = this._heap.pop();
    if (this._heap.length > 0) {
      this._heap[0] = last;
      this._siftDown(0);
    }
    return top;
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this._heap[parent].priority >= this._heap[i].priority) break;
      [this._heap[parent], this._heap[i]] = [this._heap[i], this._heap[parent]];
      i = parent;
    }
  }

  _siftDown(i) {
    const n = this._heap.length;
    while (true) {
      let largest = i;
      const l = 2 * i + 1;
      const r = 2 * i + 2;
      if (l < n && this._heap[l].priority > this._heap[largest].priority)
        largest = l;
      if (r < n && this._heap[r].priority > this._heap[largest].priority)
        largest = r;
      if (largest === i) break;
      [this._heap[largest], this._heap[i]] = [this._heap[i], this._heap[largest]];
      i = largest;
    }
  }
}

// Export a singleton so every module shares the same queue.
module.exports = new QueueSystem();
module.exports.STATUS = STATUS;
module.exports.QueueSystem = QueueSystem;
