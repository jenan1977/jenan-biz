/**
 * design-endpoint.js - Brand Design AI robot routes.
 *
 * POST /api/design/analyze    → Enqueue design analysis job, return jobId
 * GET  /api/design/jobs/:jobId → Return job status and result
 */

const express = require('express');
const { handle, getJobStatus } = require('../request-handler');

const router = express.Router();

/**
 * Build user message from brand information fields.
 */
function buildUserMessage(body) {
  const fields = [
    ['اسم العلامة التجارية', body.brand_name],
    ['وصف العلامة التجارية', body.brand_description],
    ['القطاع / الصناعة', body.industry],
    ['الجمهور المستهدف', body.target_audience],
    ['قيم العلامة التجارية', body.brand_values],
    ['شخصية العلامة التجارية', body.brand_personality],
    ['الألوان المفضلة', body.preferred_colors],
    ['الأسلوب البصري المفضل', body.visual_style],
    ['المنافسون', body.competitors],
    ['ما يميزها عن المنافسين', body.differentiators],
    ['المنصات المستهدفة', body.platforms],
    ['اللغة الرئيسية', body.primary_language],
    ['شعار موجود؟', body.has_existing_logo],
    ['ملاحظات إضافية', body.additional_notes],
  ];

  const lines = fields
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([label, value]) => `${label}: ${value}`);

  return `يرجى تحليل العلامة التجارية التالية وتقديم توصيات تصميمية شاملة:\n\n${lines.join('\n')}`;
}

// POST /api/design/analyze
router.post('/analyze', (req, res, next) => {
  try {
    const body = req.body || {};

    if (!body.brand_name && !body.brand_description) {
      return res.status(400).json({
        error: 'يجب توفير اسم العلامة التجارية أو وصفها على الأقل.',
        code: 'VALIDATION_ERROR',
      });
    }

    const userMessage = buildUserMessage(body);
    const jobId = handle('design', userMessage, 7);

    console.log(`[Design] New job enqueued: ${jobId}`);
    return res.status(202).json({ jobId, status: 'pending' });
  } catch (err) {
    return next(err);
  }
});

// GET /api/design/jobs/:jobId
router.get('/jobs/:jobId', (req, res, next) => {
  try {
    const { jobId } = req.params;
    const job = getJobStatus(jobId);

    if (!job) {
      return res.status(404).json({ error: 'الطلب غير موجود.', code: 'JOB_NOT_FOUND' });
    }

    return res.json(job);
  } catch (err) {
    return next(err);
  }
});

module.exports = router;
