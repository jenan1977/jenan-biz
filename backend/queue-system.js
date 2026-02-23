/**
 * queue-system.js - Priority queue with concurrency control and automatic retry.
 *
 * Features:
 *  - Priority Queue (higher priority processed first)
 *  - Configurable max concurrency (default 1000 to serve up to 1000 simultaneous
 *    clients; each job awaits its own OpenAI call so the effective API concurrency
 *    is bounded by your OpenAI rate limits — lower QUEUE_MAX_CONCURRENCY in .env
 *    if you need to stay well within those limits)
 *  - Job status tracking: pending, processing, completed, failed
 *  - Automatic retry with exponential backoff (max 5 attempts)
 *  - EventEmitter notifications
 */

const EventEmitter = require('events');
const { v4: uuidv4 } = require('uuid');
const { config } = require('./config');

const JOB_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

class QueueSystem extends EventEmitter {
  constructor(options = {}) {
    super();
    this._maxConcurrency = options.maxConcurrency || config.QUEUE_MAX_CONCURRENCY;
    this._maxAttempts = options.maxAttempts || config.QUEUE_MAX_ATTEMPTS;
    this._baseDelayMs = options.baseDelayMs || config.QUEUE_BASE_DELAY_MS;

    /** @type {Map<string, object>} jobId -> job metadata */
    this._jobs = new Map();

    /** @type {Array<object>} sorted heap (max-heap by priority) */
    this._pending = [];

    /** @type {number} */
    this._active = 0;
  }

  /**
   * Add a job to the queue.
   *
   * @param {Function} task       - Async function to execute.
   * @param {object}   options
   * @param {number}   [options.priority=5]  - Higher value = processed sooner.
   * @param {string}   [options.jobId]       - Custom job ID (auto-generated if omitted).
   * @returns {string} jobId
   */
  enqueue(task, options = {}) {
    const jobId = options.jobId || uuidv4();
    const priority = typeof options.priority === 'number' ? options.priority : 5;

    const job = {
      id: jobId,
      task,
      priority,
      attempts: 0,
      status: JOB_STATUS.PENDING,
      createdAt: new Date(),
      startedAt: null,
      finishedAt: null,
      result: null,
      error: null,
    };

    this._jobs.set(jobId, job);
    this._heapPush(job);
    this.emit('enqueued', { jobId, priority });
    console.log(`[Queue] Enqueued job ${jobId} (priority=${priority})`);

    // Kick off processing without blocking
    setImmediate(() => this._tick());

    return jobId;
  }

  /**
   * Get the current status of a job.
   *
   * @param {string} jobId
   * @returns {object|null}
   */
  getJob(jobId) {
    const job = this._jobs.get(jobId);
    if (!job) return null;
    return {
      id: job.id,
      status: job.status,
      attempts: job.attempts,
      createdAt: job.createdAt,
      startedAt: job.startedAt,
      finishedAt: job.finishedAt,
      result: job.result,
      error: job.error,
    };
  }

  /** @returns {number} Number of jobs currently being processed */
  get activeCount() {
    return this._active;
  }

  /** @returns {number} Number of jobs waiting in the queue */
  get pendingCount() {
    return this._pending.length;
  }

  // ─── Internal ───────────────────────────────────────────────────────────────

  _tick() {
    while (this._active < this._maxConcurrency && this._pending.length > 0) {
      const job = this._heapPop();
      if (!job) break;
      this._run(job);
    }
  }

  async _run(job) {
    this._active++;
    job.status = JOB_STATUS.PROCESSING;
    job.startedAt = new Date();
    job.attempts++;
    this.emit('processing', { jobId: job.id, attempt: job.attempts });
    console.log(`[Queue] Processing job ${job.id} (attempt ${job.attempts}/${this._maxAttempts})`);

    try {
      job.result = await job.task();
      job.status = JOB_STATUS.COMPLETED;
      job.finishedAt = new Date();
      this.emit('completed', { jobId: job.id, result: job.result });
      console.log(`[Queue] Completed job ${job.id}`);
    } catch (err) {
      job.error = err.message || String(err);
      if (job.attempts < this._maxAttempts) {
        const delay = this._baseDelayMs * Math.pow(2, job.attempts - 1);
        job.status = JOB_STATUS.PENDING;
        console.log(
          `[Queue] Job ${job.id} failed (attempt ${job.attempts}). Retrying in ${delay}ms...`
        );
        this.emit('retry', { jobId: job.id, attempt: job.attempts, delay });
        setTimeout(() => {
          this._heapPush(job);
          this._tick();
        }, delay);
      } else {
        job.status = JOB_STATUS.FAILED;
        job.finishedAt = new Date();
        this.emit('failed', { jobId: job.id, error: job.error });
        console.log(`[Queue] Job ${job.id} permanently failed: ${job.error}`);
      }
    } finally {
      this._active--;
      this._tick();
    }
  }

  // ─── Max-heap helpers ────────────────────────────────────────────────────────

  _heapPush(job) {
    this._pending.push(job);
    this._bubbleUp(this._pending.length - 1);
  }

  _heapPop() {
    if (this._pending.length === 0) return null;
    const top = this._pending[0];
    const last = this._pending.pop();
    if (this._pending.length > 0) {
      this._pending[0] = last;
      this._sinkDown(0);
    }
    return top;
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (this._pending[parent].priority >= this._pending[i].priority) break;
      [this._pending[parent], this._pending[i]] = [this._pending[i], this._pending[parent]];
      i = parent;
    }
  }

  _sinkDown(i) {
    const n = this._pending.length;
    while (true) {
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      let largest = i;
      if (left < n && this._pending[left].priority > this._pending[largest].priority) largest = left;
      if (right < n && this._pending[right].priority > this._pending[largest].priority) largest = right;
      if (largest === i) break;
      [this._pending[i], this._pending[largest]] = [this._pending[largest], this._pending[i]];
      i = largest;
    }
  }
}

// Singleton queue instance
const queue = new QueueSystem();

module.exports = { QueueSystem, queue, JOB_STATUS };
