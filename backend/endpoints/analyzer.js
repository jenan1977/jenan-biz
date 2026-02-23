/**
 * analyzer.js - Project Analyzer bot endpoints.
 *
 * POST /api/analyzer/analyze  - Enqueue a project analysis job
 * GET  /api/analyzer/jobs/:jobId - Poll job status / result
 */

'use strict'

const express = require('express')
const { handle, queue } = require('../request-handler')

const router = express.Router()

// POST /api/analyzer/analyze
router.post('/analyze', async (req, res) => {
  try {
    const { projectName, description, budget, goals } = req.body

    if (!projectName || !description) {
      return res.status(400).json({ error: 'Missing required fields: projectName and description' })
    }

    const { jobId } = await handle('analyzer', req.body, 8)

    res.status(202).json({
      jobId,
      status: 'accepted',
      checkUrl: `/api/analyzer/jobs/${jobId}`
    })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// GET /api/analyzer/jobs/:jobId
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
