/**
 * courses-endpoint.js – Express router for the courses AI robot.
 *
 * Routes:
 *   POST /api/courses             Submit a course-design request
 *   GET  /api/courses/jobs/:jobId Poll job status / result
 */

"use strict";

const { Router } = require("express");
const { chatCompletion } = require("../api-client");
const { COURSES_SYSTEM_PROMPT } = require("../prompts/courses-prompt");
const { dispatchJob, pollStatus } = require("../request-handler");
const { asyncWrap } = require("../utils/error-handler");
const { bodyValidator, validateChatRequest } = require("../utils/validators");
const logger = require("../utils/logger");

const router = Router();

// ── POST /api/courses ─────────────────────────────────────────────────────────

router.post(
  "/",
  bodyValidator(validateChatRequest),
  asyncWrap(async (req, res) => {
    const { message, context = {}, priority = 5 } = req.body;

    let userPrompt = message;
    if (Object.keys(context).length > 0) {
      const ctxLines = Object.entries(context)
        .map(([k, v]) => `- ${k}: ${v}`)
        .join("\n");
      userPrompt = `${message}\n\n**تفاصيل الدورة:**\n${ctxLines}`;
    }

    const jobFn = async () => {
      logger.info("Running courses job");
      const result = await chatCompletion({
        systemPrompt: COURSES_SYSTEM_PROMPT,
        userMessage: userPrompt,
      });
      return { course: result };
    };

    dispatchJob(res, jobFn, { priority });
  })
);

// ── GET /api/courses/jobs/:jobId ──────────────────────────────────────────────

router.get("/jobs/:jobId", asyncWrap(pollStatus));

module.exports = router;
