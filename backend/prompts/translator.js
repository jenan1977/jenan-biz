"use strict";
/**
 * translator.js - System prompt for translating content.
 */

const LANGUAGE_NAMES = {
  ar: "العربية",
  en: "الإنجليزية",
  fr: "الفرنسية",
  de: "الألمانية",
  tr: "التركية",
  es: "الإسبانية",
};

/**
 * Build the system prompt for translation.
 * @param {object} options
 * @param {string} [options.targetLanguage] - Target language code ("en", "ar", etc.).
 * @returns {string}
 */
function translatorPrompt({ targetLanguage = "en" } = {}) {
  const langName = LANGUAGE_NAMES[targetLanguage] || targetLanguage;
  return `أنت مترجم محترف متخصص في ترجمة المحتوى التجاري والمالي.
مهمتك: ترجمة المحتوى المقدم إلى ${langName} بدقة واحترافية.

### معايير الترجمة:
- الحفاظ على تنسيق Markdown كما هو
- ترجمة طبيعية وليست حرفية
- الحفاظ على المصطلحات التقنية والمالية المعيارية
- الحفاظ على الأرقام والبيانات دون تعديل

### صيغة الإخراج (JSON إلزامي):
{
  "translated_content": "المحتوى المترجم",
  "target_language": "${targetLanguage}",
  "notes": "ملاحظات المترجم (اختياري)"
}`;
}

module.exports = { translatorPrompt };
