"use strict";
/**
 * ai-translator.js - Translate a blog article using OpenAI.
 *
 * POST /api/blog/ai/translate/:id
 * Body: { content, targetLanguage }
 */

const { OpenAI } = require("openai");
const { translatorPrompt } = require("../prompts/translator");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

/**
 * Translate article content.
 * @param {object} options
 * @param {string} options.content          - Original content.
 * @param {string} [options.targetLanguage] - Target language code ("en", "ar", "fr", etc.).
 * @returns {Promise<{translated_content:string, target_language:string}>}
 */
async function translateArticle({ content, targetLanguage = "en" }) {
  const systemPrompt = translatorPrompt({ targetLanguage });

  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    temperature: 0.3,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: content },
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
    const { content, targetLanguage } = req.body;
    if (!content) {
      return res.status(400).json({ error: "content is required" });
    }
    const result = await translateArticle({ content, targetLanguage });
    return res.status(200).json(result);
  } catch (err) {
    console.error("[ai-translator] Error:", err.message);
    return res.status(500).json({ error: "Failed to translate article", details: err.message });
  }
}

module.exports = { translateArticle, handler };
