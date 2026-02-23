/**
 * courses-endpoint.js - Courses AI robot routes.
 *
 * POST /api/courses/create    → Enqueue course creation job, return jobId
 * GET  /api/courses/jobs/:jobId → Return job status and result
 */

const express = require('express');
const { handle, getJobStatus } = require('../request-handler');

const router = express.Router();

/**
 * Build user message from course information fields.
 */
function buildUserMessage(body) {
  const fields = [
    ['عنوان الدورة', body.course_title],
    ['وصف الدورة', body.course_description],
    ['المجال / التخصص', body.subject_area],
    ['الفئة المستهدفة', body.target_audience],
    ['المستوى', body.level],
    ['المتطلبات الأساسية', body.prerequisites],
    ['مدة الدورة المتوقعة', body.duration],
    ['أهداف التعلم', body.learning_objectives],
    ['المواضيع الرئيسية', body.main_topics],
    ['أسلوب التدريس المفضل', body.teaching_style],
    ['نوع المحتوى', body.content_type],
    ['الأنشطة التفاعلية', body.interactive_activities],
    ['أسلوب التقييم', body.assessment_method],
    ['اللغة', body.language],
    ['المنصة المستهدفة', body.platform],
    ['ملاحظات إضافية', body.additional_notes],
  ];

  const lines = fields
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([label, value]) => `${label}: ${value}`);

  return `يرجى إنشاء خطة دورة تعليمية شاملة بناءً على المعلومات التالية:\n\n${lines.join('\n')}`;
}

// POST /api/courses/create
router.post('/create', (req, res, next) => {
  try {
    const body = req.body || {};

    if (!body.course_title && !body.course_description) {
      return res.status(400).json({
        error: 'يجب توفير عنوان الدورة أو وصفها على الأقل.',
        code: 'VALIDATION_ERROR',
      });
    }

    const userMessage = buildUserMessage(body);
    const jobId = handle('courses', userMessage, 6);

    console.log(`[Courses] New job enqueued: ${jobId}`);
    return res.status(202).json({ jobId, status: 'pending' });
  } catch (err) {
    return next(err);
  }
});

// GET /api/courses/jobs/:jobId
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
