/**
 * design-endpoint.js - Express router for the Design Studio robot.
 *
 * POST /api/design
 *   Body: { designBrief, [brandName], [industry], [targetAudience],
 *           [colorPreferences], [style], [priority] }
 *
 * Returns: { success: true, requestId, result }  (or error payload)
 */

"use strict";

const express = require("express");
const requestHandler = require("../request-handler");
const { validateDesignRequest } = require("../utils/validators");

const router = express.Router();

router.post("/", async (req, res, next) => {
  try {
    const data = validateDesignRequest(req.body);

    const userMessage = buildUserMessage(data);

    const { requestId, result } = await requestHandler.handle({
      type: "design",
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
  const lines = [`موجز التصميم: ${data.designBrief}`];

  if (data.brandName) lines.push(`اسم العلامة التجارية: ${data.brandName}`);
  if (data.industry) lines.push(`القطاع: ${data.industry}`);
  if (data.targetAudience) lines.push(`الجمهور المستهدف: ${data.targetAudience}`);
  if (data.colorPreferences)
    lines.push(`تفضيلات الألوان: ${data.colorPreferences}`);
  if (data.style) lines.push(`الأسلوب المفضل: ${data.style}`);
  if (data.competitors) lines.push(`المنافسون: ${data.competitors}`);
  if (data.values) lines.push(`قيم العلامة التجارية: ${data.values}`);

  lines.push(
    "\nالمطلوب: توجيهات تصميم شاملة تشمل الألوان والخطوط وعناصر الهوية البصرية."
  );

  return lines.join("\n");
}

module.exports = router;
