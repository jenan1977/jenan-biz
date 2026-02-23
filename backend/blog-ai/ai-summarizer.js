"use strict";
/**
 * ai-summarizer.js - Summarize a blog article using OpenAI.
 *
 * POST /api/blog/ai/summarize/:id
 * Body: { content, maxLength }
 */

const { OpenAI } = require("openai");

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const SYSTEM_PROMPT = `أنت مساعد ذكي متخصص في تلخيص المقالات باللغة العربية.
مهمتك: إنشاء ملخص احترافي وموجز للمقالة المقدمة.
الشروط:
- الملخص يجب أن يكون باللغة العربية الفصحى
- استخدم نقاط مرتبة لتسهيل القراءة
- ركّز على الأفكار الرئيسية فقط
- أعِد النتيجة بصيغة JSON: {"summary": "...", "key_points": ["...", "..."], "reading_time_minutes": N}`;

/**
 * Summarize an article.
 * @param {object} options
 * @param {string} options.content    - The article content.
 * @param {number} [options.maxLength] - Max summary length in words.
 * @returns {Promise<{summary:string, key_points:string[], reading_time_minutes:number}>}
 */
async function summarizeArticle({ content, maxLength = 200 }) {
  const completion = await openai.chat.completions.create({
    model: "gpt-4o",
    temperature: 0.3,
    response_format: { type: "json_object" },
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      {
        role: "user",
        content: `لخّص المقالة التالية في حدود ${maxLength} كلمة:\n\n${content}`,
      },
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
    const { content, maxLength } = req.body;
    if (!content) {
      return res.status(400).json({ error: "content is required" });
    }
    const result = await summarizeArticle({ content, maxLength });
    return res.status(200).json(result);
  } catch (err) {
    console.error("[ai-summarizer] Error:", err.message);
    return res.status(500).json({ error: "Failed to summarize article", details: err.message });
  }
}

module.exports = { summarizeArticle, handler };
