/**
 * analyzer-endpoint.js - Express router for the Project Analyzer robot.
 *
 * POST /api/analyze
 *   Body: { projectName, projectDescription, [industry], [targetMarket],
 *           [budget], [timeline], [priority] }
 *
 * Returns: { success: true, requestId, result }  (or error payload)
 */

"use strict";

const express = require("express");
const requestHandler = require("../request-handler");
const { validateAnalyzerRequest } = require("../utils/validators");

const router = express.Router();

router.post("/", async (req, res, next) => {
  try {
    const data = validateAnalyzerRequest(req.body);

    const userMessage = buildUserMessage(data);

    const { requestId, result } = await requestHandler.handle({
      type: "analyzer",
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
  const lines = [
    `اسم المشروع: ${data.projectName}`,
    `وصف المشروع: ${data.projectDescription}`,
  ];

  if (data.industry) lines.push(`القطاع: ${data.industry}`);
  if (data.targetMarket) lines.push(`السوق المستهدف: ${data.targetMarket}`);
  if (data.budget) lines.push(`الميزانية: ${data.budget}`);
  if (data.timeline) lines.push(`الجدول الزمني: ${data.timeline}`);
  if (data.teamSize) lines.push(`حجم الفريق: ${data.teamSize}`);
  if (data.currentRevenue) lines.push(`الإيرادات الحالية: ${data.currentRevenue}`);
  if (data.goals) lines.push(`الأهداف: ${data.goals}`);
  if (data.challenges) lines.push(`التحديات: ${data.challenges}`);

  lines.push(
    "\nالمطلوب: تحليل شامل للمشروع مع دراسة الجدوى والتوصيات الاستراتيجية."
  );

  return lines.join("\n");
}

module.exports = router;
