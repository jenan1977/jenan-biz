"use strict";
/**
 * ai-generator.js - Generate new blog articles using OpenAI.
 *
 * POST /api/blog/ai/generate
 * Body: { topic, category, language, wordCount }
 */

const { OpenAI } = require("openai");
const { blogArticleGeneratorPrompt } = require("../prompts/blog-article-generator");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

/**
 * Generate a full blog article for the given topic.
 * @param {object} options
 * @param {string} options.topic        - The article topic.
 * @param {string} [options.category]   - Optional category hint.
 * @param {string} [options.language]   - "ar" (default) or "en".
 * @param {number} [options.wordCount]  - Approximate target word count.
 * @returns {Promise<{title:string, slug:string, content:string, excerpt:string, tags:string[]}>}
 */
async function generateArticle({ topic, category = "", language = "ar", wordCount = 1500 }) {
  const systemPrompt = blogArticleGeneratorPrompt({ language, wordCount });
  const userMessage = category
    ? `اكتب مقالة عن: "${topic}" ضمن فئة: "${category}"`
    : `اكتب مقالة عن: "${topic}"`;

  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    temperature: 0.7,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userMessage },
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
    const { topic, category, language, wordCount } = req.body;
    if (!topic) {
      return res.status(400).json({ error: "topic is required" });
    }
    const article = await generateArticle({ topic, category, language, wordCount });
    return res.status(200).json(article);
  } catch (err) {
    console.error("[ai-generator] Error:", err.message);
    return res.status(500).json({ error: "Failed to generate article", details: err.message });
  }
}

module.exports = { generateArticle, handler };
