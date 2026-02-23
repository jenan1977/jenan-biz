"use strict";
/**
 * content-improver.js - System prompt for improving existing content.
 */

/**
 * Build the system prompt for content improvement.
 * @param {object} options
 * @param {string[]} [options.focusAreas] - Areas to focus on.
 * @returns {string}
 */
function contentImproverPrompt({ focusAreas = ["grammar", "readability"] } = {}) {
  const focusMap = {
    grammar: "تصحيح الأخطاء النحوية والإملائية",
    readability: "تحسين الأسلوب وسهولة القراءة",
    seo: "تحسين الكلمات المفتاحية والبنية للـ SEO",
    length: "توسيع المحتوى وإضافة تفاصيل مفيدة",
    structure: "إعادة هيكلة المحتوى بشكل أوضح",
  };

  const focusList = focusAreas
    .map((area) => `- ${focusMap[area] || area}`)
    .join("\n");

  return `أنت محرر محتوى متخصص في تحسين المقالات العربية لمدونة أعمال احترافية.
مهمتك: تحسين المقالة المقدمة مع التركيز على:
${focusList}

### شروط التحسين:
- الحفاظ على المعنى والأفكار الأصلية
- عدم حذف معلومات جوهرية
- استخدام لغة عربية فصيحة وحديثة
- إبقاء الأرقام والإحصاءات كما هي

### صيغة الإخراج (JSON إلزامي):
{
  "improved_content": "المحتوى المحسّن كاملاً",
  "changes_summary": "ملخص التغييرات التي أُجريت",
  "improvement_score": "تقدير نسبة التحسين (1-100)"
}`;
}

module.exports = { contentImproverPrompt };
