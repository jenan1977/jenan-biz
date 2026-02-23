/**
 * server.js - Main Express server for Jenan Biz AI system.
 *
 * Supports 20,000 concurrent requests via the priority queue system.
 */

'use strict'

const express = require('express')
const cors = require('cors')
require('dotenv').config()

const config = require('./backend/config')
const analyzerRouter = require('./backend/endpoints/analyzer')
const designRouter = require('./backend/endpoints/design')
const coursesRouter = require('./backend/endpoints/courses')

const app = express()

// Middleware
app.use(cors())
app.use(express.json({ limit: '50mb' }))
app.use(express.urlencoded({ limit: '50mb', extended: true }))

// Static files
app.use(express.static('pages'))

// Routes
app.use('/api/analyzer', analyzerRouter)
app.use('/api/design', designRouter)
app.use('/api/courses', coursesRouter)

// Health check
app.get('/health', (req, res) => {
  const { queue } = require('./backend/request-handler')
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    queue: queue.stats()
  })
})

// Home page
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/pages/projects-analyzer.html')
})

// 404
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' })
})

// Error handling
app.use((err, req, res, next) => { // eslint-disable-line no-unused-vars
  console.error(err)
  res.status(500).json({ error: 'Internal server error' })
})

// Graceful shutdown
const server = app.listen(config.server.port, config.server.host, () => {
  console.log(`🚀 Server running on http://${config.server.host}:${config.server.port}`)
})

process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down...')
  const { queue } = require('./backend/request-handler')
  queue.destroy()
  server.close(() => {
    console.log('Server closed')
    process.exit(0)
  })
})

module.exports = app
