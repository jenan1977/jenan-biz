/**
 * analyzer-endpoint.js – Express router for the project-analysis AI robot.
 *
 * Routes:
 *   POST /api/analyzer          Submit a project analysis request
 *   GET  /api/analyzer/jobs/:jobId  Poll job status / result
 */

"use strict";

const { Router } = require("express");
const { chatCompletion } = require("../api-client");
const { ANALYZER_SYSTEM_PROMPT } = require("../prompts/analyzer-prompt");
const { dispatchJob, pollStatus } = require("../request-handler");
const { asyncWrap } = require("../utils/error-handler");
const { bodyValidator, validateAnalyzeRequest } = require("../utils/validators");
const logger = require("../utils/logger");

const router = Router();

// ── POST /api/analyzer ────────────────────────────────────────────────────────

router.post(
  "/",
  bodyValidator(validateAnalyzeRequest),
  asyncWrap(async (req, res) => {
    const { message, context = {}, priority = 5 } = req.body;

    // Build a rich user prompt combining the free-text message and any
    // structured context fields the client provided.
    let userPrompt = message;
    if (Object.keys(context).length > 0) {
      const ctxLines = Object.entries(context)
        .map(([k, v]) => `- ${k}: ${v}`)
        .join("\n");
      userPrompt = `${message}\n\n**بيانات المشروع:**\n${ctxLines}`;
    }

    const jobFn = async () => {
      logger.info("Running analyzer job");
      const result = await chatCompletion({
        systemPrompt: ANALYZER_SYSTEM_PROMPT,
        userMessage: userPrompt,
      });
      return { analysis: result };
    };

    dispatchJob(res, jobFn, { priority });
  })
);

// ── GET /api/analyzer/jobs/:jobId ─────────────────────────────────────────────

router.get("/jobs/:jobId", asyncWrap(pollStatus));

module.exports = router;
