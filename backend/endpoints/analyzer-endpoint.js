/**
 * analyzer-endpoint.js - Project Analyzer AI robot routes.
 *
 * POST /api/analyzer/analyze  → Enqueue analysis job, return jobId
 * GET  /api/analyzer/jobs/:jobId → Return job status and result
 */

const express = require('express');
const { handle, getJobStatus } = require('../request-handler');

const router = express.Router();

/**
 * Validate and format project data fields into a user message string.
 */
function buildUserMessage(body) {
  const fields = [
    ['اسم المشروع', body.project_name],
    ['وصف المشروع', body.project_description],
    ['القطاع / الصناعة', body.industry],
    ['الموقع الجغرافي', body.location],
    ['الفئة المستهدفة', body.target_audience],
    ['حجم السوق المستهدف', body.market_size],
    ['المنافسون الرئيسيون', body.competitors],
    ['المميزات التنافسية', body.competitive_advantages],
    ['رأس المال الأولي', body.initial_capital],
    ['مصادر التمويل', body.funding_sources],
    ['نموذج الإيراد', body.revenue_model],
    ['التوقعات المالية', body.financial_projections],
    ['فريق العمل', body.team],
    ['الخبرات المتوفرة', body.existing_expertise],
    ['المرحلة الحالية', body.current_stage],
    ['الأهداف قصيرة المدى', body.short_term_goals],
    ['الأهداف طويلة المدى', body.long_term_goals],
    ['التحديات المتوقعة', body.challenges],
    ['القيود التنظيمية', body.regulatory_constraints],
    ['المنتجات / الخدمات', body.products_services],
    ['قنوات التوزيع', body.distribution_channels],
    ['استراتيجية التسويق', body.marketing_strategy],
    ['شراكات محتملة', body.potential_partnerships],
    ['التكنولوجيا المستخدمة', body.technology_used],
    ['الاستدامة والمسؤولية الاجتماعية', body.sustainability],
    ['الجدول الزمني للمشروع', body.timeline],
    ['مقاييس النجاح', body.success_metrics],
    ['مخاطر المشروع', body.risks],
    ['استراتيجية الخروج', body.exit_strategy],
    ['ملاحظات إضافية', body.additional_notes],
  ];

  const lines = fields
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([label, value]) => `${label}: ${value}`);

  return `يرجى تحليل المشروع التالي وتقديم تقرير شامل:\n\n${lines.join('\n')}`;
}

// POST /api/analyzer/analyze
router.post('/analyze', (req, res, next) => {
  try {
    const body = req.body || {};

    if (!body.project_name && !body.project_description) {
      return res.status(400).json({
        error: 'يجب توفير اسم المشروع أو وصفه على الأقل.',
        code: 'VALIDATION_ERROR',
      });
    }

    const userMessage = buildUserMessage(body);
    const jobId = handle('analyzer', userMessage, 8);

    console.log(`[Analyzer] New job enqueued: ${jobId}`);
    return res.status(202).json({ jobId, status: 'pending' });
  } catch (err) {
    return next(err);
  }
});

// GET /api/analyzer/jobs/:jobId
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
