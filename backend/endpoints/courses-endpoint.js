/**
 * courses-endpoint.js - Express router for the Daily Courses robot.
 *
 * POST /api/courses
 *   Body: { topic, [level], [availableHoursPerDay], [durationWeeks],
 *           [goals], [currentKnowledge], [priority] }
 *
 * Returns: { success: true, requestId, result }  (or error payload)
 */

"use strict";

const express = require("express");
const requestHandler = require("../request-handler");
const { validateCoursesRequest } = require("../utils/validators");

const router = express.Router();

router.post("/", async (req, res, next) => {
  try {
    const data = validateCoursesRequest(req.body);

    const userMessage = buildUserMessage(data);

    const { requestId, result } = await requestHandler.handle({
      type: "courses",
      userMessage,
      priority: data.priority,
    });

    res.json({ success: true, requestId, result });
  } catch (err) {
    next(err);
  }
});

// ── Helpers ──────────────────────────────────────────────────────────────────

function buildUserMessage(data) {
  const lines = [`الموضوع / المهارة المطلوبة: ${data.topic}`];

  if (data.level) lines.push(`المستوى الحالي: ${data.level}`);
  if (data.availableHoursPerDay)
    lines.push(`الوقت المتاح يوميًا: ${data.availableHoursPerDay} ساعة`);
  if (data.durationWeeks)
    lines.push(`مدة التعلم المستهدفة: ${data.durationWeeks} أسبوع`);
  if (data.goals) lines.push(`الأهداف من التعلم: ${data.goals}`);
  if (data.currentKnowledge)
    lines.push(`المعرفة الحالية: ${data.currentKnowledge}`);
  if (data.preferredResources)
    lines.push(`المصادر المفضلة: ${data.preferredResources}`);

  lines.push(
    "\nالمطلوب: خطة تعليمية مخصصة يومية/أسبوعية مع مصادر وتحديات عملية."
  );

  return lines.join("\n");
}

module.exports = router;
