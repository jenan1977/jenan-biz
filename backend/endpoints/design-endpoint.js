/**
 * design-endpoint.js – Express router for the design AI robot.
 *
 * Routes:
 *   POST /api/design             Submit a design request
 *   GET  /api/design/jobs/:jobId Poll job status / result
 */

"use strict";

const { Router } = require("express");
const { chatCompletion } = require("../api-client");
const { DESIGN_SYSTEM_PROMPT } = require("../prompts/design-prompt");
const { dispatchJob, pollStatus } = require("../request-handler");
const { asyncWrap } = require("../utils/error-handler");
const { bodyValidator, validateChatRequest } = require("../utils/validators");
const logger = require("../utils/logger");

const router = Router();

// ── POST /api/design ──────────────────────────────────────────────────────────

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
      userPrompt = `${message}\n\n**تفاصيل المشروع:**\n${ctxLines}`;
    }

    const jobFn = async () => {
      logger.info("Running design job");
      const result = await chatCompletion({
        systemPrompt: DESIGN_SYSTEM_PROMPT,
        userMessage: userPrompt,
      });
      return { design: result };
    };

    dispatchJob(res, jobFn, { priority });
  })
);

// ── GET /api/design/jobs/:jobId ───────────────────────────────────────────────

router.get("/jobs/:jobId", asyncWrap(pollStatus));

module.exports = router;
