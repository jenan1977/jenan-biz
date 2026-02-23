"use strict";
/**
 * ai-improver.js - Improve an existing blog article using OpenAI.
 *
 * POST /api/blog/ai/improve/:id
 * Body: { content, focusAreas[] }
 */

const { OpenAI } = require("openai");
const { contentImproverPrompt } = require("../prompts/content-improver");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

/**
 * Improve an article's content.
 * @param {object} options
 * @param {string} options.content      - The original article content.
 * @param {string[]} [options.focusAreas] - Areas to focus on: "grammar", "seo", "readability", "length".
 * @returns {Promise<{improved_content:string, changes_summary:string}>}
 */
async function improveArticle({ content, focusAreas = ["grammar", "readability"] }) {
  const systemPrompt = contentImproverPrompt({ focusAreas });

  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    temperature: 0.5,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: `قم بتحسين المقالة التالية:\n\n${content}` },
    ],
  });

  const raw = completion.choices[0].message.content;
  return JSON.parse(raw);
}

/**
 * Express route handler.
 */
async function handler(req, res) {
  try {
    const { content, focusAreas } = req.body;
    if (!content) {
      return res.status(400).json({ error: "content is required" });
    }
    const result = await improveArticle({ content, focusAreas });
    return res.status(200).json(result);
  } catch (err) {
    console.error("[ai-improver] Error:", err.message);
    return res.status(500).json({ error: "Failed to improve article", details: err.message });
  }
}

module.exports = { improveArticle, handler };
