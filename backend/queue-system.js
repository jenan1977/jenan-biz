/**
 * queue-system.js - Priority Queue with concurrency control for 20K concurrent requests.
 *
 * Features:
 * - Max-heap priority queue (higher number = higher priority)
 * - Concurrency control (max active jobs configurable)
 * - Max queue size: 20,000
 * - Exponential backoff retry (max 3 attempts)
 * - Job status tracking: pending, processing, completed, failed
 * - Memory optimization: remove completed/failed jobs after 5 mins
 * - EventEmitter for job notifications
 */

'use strict'

const { EventEmitter } = require('events')

class PriorityQueue {
  constructor () {
    this._heap = []
  }

  get size () {
    return this._heap.length
  }

  push (item) {
    this._heap.push(item)
    this._bubbleUp(this._heap.length - 1)
  }

  pop () {
    if (this._heap.length === 0) return undefined
    const top = this._heap[0]
    const last = this._heap.pop()
    if (this._heap.length > 0) {
      this._heap[0] = last
      this._siftDown(0)
    }
    return top
  }

  _bubbleUp (idx) {
    while (idx > 0) {
      const parent = (idx - 1) >> 1
      if (this._heap[parent].priority >= this._heap[idx].priority) break
      ;[this._heap[parent], this._heap[idx]] = [this._heap[idx], this._heap[parent]]
      idx = parent
    }
  }

  _siftDown (idx) {
    const n = this._heap.length
    while (true) {
      let largest = idx
      const left = 2 * idx + 1
      const right = 2 * idx + 2
      if (left < n && this._heap[left].priority > this._heap[largest].priority) largest = left
      if (right < n && this._heap[right].priority > this._heap[largest].priority) largest = right
      if (largest === idx) break
      ;[this._heap[largest], this._heap[idx]] = [this._heap[idx], this._heap[largest]]
      idx = largest
    }
  }
}

class Queue extends EventEmitter {
  /**
   * @param {object} [options]
   * @param {number} [options.maxSize=20000]   Maximum queued jobs.
   * @param {number} [options.concurrency=150] Maximum simultaneous active jobs.
   * @param {number} [options.retryLimit=3]    Max retry attempts per job.
   * @param {number} [options.retryDelay=1000] Base delay (ms) for exponential backoff.
   * @param {number} [options.ttl=300000]      TTL (ms) for completed/failed jobs (default 5 min).
   */
  constructor (options = {}) {
    super()
    this._maxSize = options.maxSize || 20000
    this._concurrency = options.concurrency || 150
    this._retryLimit = options.retryLimit || 3
    this._retryDelay = options.retryDelay || 1000
    this._ttl = options.ttl || 5 * 60 * 1000

    this._pq = new PriorityQueue()
    this._jobs = new Map()   // jobId -> job metadata
    this._active = 0
    this._jobCounter = 0

    // Periodically purge completed/failed jobs to keep memory bounded
    this._cleanupInterval = setInterval(() => this._cleanup(), 60 * 1000)
    if (this._cleanupInterval.unref) this._cleanupInterval.unref()
  }

  /**
   * Enqueue a job function.
   *
   * @param {Function} fn        Async function to execute.
   * @param {number}   [priority=5]  Priority (higher = sooner). Range 1–10.
   * @returns {string} jobId
   * @throws  {Error}  When the queue is full.
   */
  enqueue (fn, priority = 5) {
    if (this._pq.size >= this._maxSize) {
      throw new Error(`Queue is full (max ${this._maxSize} jobs)`)
    }

    const jobId = String(++this._jobCounter)
    const job = {
      id: jobId,
      fn,
      priority,
      status: 'pending',
      attempts: 0,
      result: null,
      error: null,
      createdAt: Date.now(),
      finishedAt: null
    }

    this._jobs.set(jobId, job)
    this._pq.push({ jobId, priority })
    this._tick()
    return jobId
  }

  /**
   * Return the status string for a job, or undefined if not found.
   * @param {string} jobId
   * @returns {string|undefined}
   */
  getJobStatus (jobId) {
    const job = this._jobs.get(jobId)
    return job ? job.status : undefined
  }

  /**
   * Return the full job object, or undefined if not found.
   * @param {string} jobId
   * @returns {object|undefined}
   */
  getJob (jobId) {
    return this._jobs.get(jobId)
  }

  /**
   * Returns queue statistics.
   */
  stats () {
    return {
      queued: this._pq.size,
      active: this._active,
      total: this._jobs.size
    }
  }

  // ── private ───────────────────────────────────────────────────────────────

  _tick () {
    while (this._active < this._concurrency && this._pq.size > 0) {
      const { jobId } = this._pq.pop()
      const job = this._jobs.get(jobId)

      // Job may have been removed already (edge case)
      if (!job) continue

      this._active++
      job.status = 'processing'
      this._run(job)
    }
  }

  async _run (job) {
    try {
      const result = await job.fn()
      job.status = 'completed'
      job.result = result
      job.finishedAt = Date.now()
      this.emit(`job:${job.id}:complete`, result)
    } catch (err) {
      job.attempts++
      if (job.attempts < this._retryLimit) {
        // Exponential backoff retry
        const delay = this._retryDelay * Math.pow(2, job.attempts - 1)
        job.status = 'pending'
        setTimeout(() => {
          this._pq.push({ jobId: job.id, priority: job.priority })
          this._tick()
        }, delay)
      } else {
        job.status = 'failed'
        job.error = err.message || String(err)
        job.finishedAt = Date.now()
        this.emit(`job:${job.id}:failed`, err)
      }
    } finally {
      this._active--
      this._tick()
    }
  }

  _cleanup () {
    const now = Date.now()
    for (const [jobId, job] of this._jobs) {
      if (
        (job.status === 'completed' || job.status === 'failed') &&
        job.finishedAt &&
        now - job.finishedAt > this._ttl
      ) {
        this._jobs.delete(jobId)
      }
    }
  }

  /**
   * Stop the cleanup interval (useful for graceful shutdown / tests).
   */
  destroy () {
    clearInterval(this._cleanupInterval)
  }
}

module.exports = Queue
