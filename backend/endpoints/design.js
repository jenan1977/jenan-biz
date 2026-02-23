/**
 * design.js - Design & branding bot endpoints.
 *
 * POST /api/design/analyze    - Enqueue a brand analysis job
 * GET  /api/design/jobs/:jobId - Poll job status / result
 */

'use strict'

const express = require('express')
const { handle, queue } = require('../request-handler')

const router = express.Router()

// POST /api/design/analyze
router.post('/analyze', async (req, res) => {
  try {
    const { brandName, description, targetAudience } = req.body

    if (!brandName || !description) {
      return res.status(400).json({ error: 'Missing required fields: brandName and description' })
    }

    const { jobId } = await handle('design', req.body, 7)

    res.status(202).json({
      jobId,
      status: 'accepted',
      checkUrl: `/api/design/jobs/${jobId}`
    })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// GET /api/design/jobs/:jobId
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
