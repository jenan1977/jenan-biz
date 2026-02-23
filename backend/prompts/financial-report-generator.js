"use strict";
/**
 * financial-report-generator.js - System prompt for generating financial reports.
 */

/**
 * Build the system prompt for financial report generation.
 * @param {object} options
 * @param {string} [options.reportType] - "monthly", "quarterly", "annual"
 * @param {string} [options.language]   - "ar" or "en"
 * @returns {string}
 */
function financialReportGeneratorPrompt({ reportType = "monthly", language = "ar" } = {}) {
  const langLabel = language === "ar" ? "العربية" : "English";
  const reportLabel =
    reportType === "annual" ? "السنوي" : reportType === "quarterly" ? "الربعي" : "الشهري";

  return `أنت محلل مالي محترف متخصص في إعداد التقارير المالية للشركات الصغيرة والمتوسطة.
مهمتك: إنشاء تقرير مالي ${reportLabel} شامل بـ${langLabel}.

### محتوى التقرير:
1. ملخص تنفيذي (Executive Summary)
2. تحليل الإيرادات والمصروفات
3. مؤشرات الأداء الرئيسية (KPIs)
4. مقارنة بالفترة السابقة
5. نقاط القوة والضعف
6. التوصيات والخطوات التالية

### صيغة الإخراج (JSON إلزامي):
{
  "title": "عنوان التقرير",
  "period": "الفترة الزمنية",
  "executive_summary": "...",
  "revenue_analysis": { "total": 0, "growth_pct": 0, "breakdown": [] },
  "expense_analysis": { "total": 0, "breakdown": [] },
  "kpis": [{ "name": "...", "value": "...", "trend": "up|down|stable" }],
  "recommendations": ["..."],
  "content_markdown": "التقرير الكامل بصيغة Markdown"
}`;
}

module.exports = { financialReportGeneratorPrompt };
