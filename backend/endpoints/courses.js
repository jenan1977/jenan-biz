/**
 * courses.js - Educational courses bot endpoints.
 *
 * POST /api/courses/create    - Enqueue a course creation job
 * GET  /api/courses/jobs/:jobId - Poll job status / result
 */

'use strict'

const express = require('express')
const { handle, queue } = require('../request-handler')

const router = express.Router()

// POST /api/courses/create
router.post('/create', async (req, res) => {
  try {
    const { topic, level, duration } = req.body

    if (!topic || !level) {
      return res.status(400).json({ error: 'Missing required fields: topic and level' })
    }

    const { jobId } = await handle('courses', req.body, 6)

    res.status(202).json({
      jobId,
      status: 'accepted',
      checkUrl: `/api/courses/jobs/${jobId}`
    })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// GET /api/courses/jobs/:jobId
router.get('/jobs/:jobId', (req, res) => {
  const job = queue.getJob(req.params.jobId)

  if (!job) {
    return res.status(404).json({ error: 'Job not found' })
  }

  res.json({
    jobId: req.params.jobId,
    status: job.status,
    result: job.result || null,
    error: job.error || null
  })
})

module.exports = router
