# Implementing Regulations — Intake Scaffold

## الغرض

هذا الدليل scaffold لاستقبال اللائحة التنفيذية لنظام الشركات السعودي (م/132، 1443هـ).
هذه مرحلة scaffold فقط — لا يوجد نص عربي مستوعب، لا ترجمة إنجليزية، لا ترجمة صينية،
لا محاذاة ثلاثية اللغة، ولا إصدار عام.

## الهيكل المقترح

```
data/implementing_regulations/
  intake_scaffold.json          ← بيانات scaffold الوصفية
  README.md                     ← هذا الملف

data/implementing_regulations/official_arabic/     (مستقبلي — غير منشأ بعد)
data/implementing_regulations/arabic_legal_llm/    (مستقبلي — غير منشأ بعد)
data/implementing_regulations/english_reference/  (مستقبلي — غير منشأ بعد)
data/implementing_regulations/english_legal_llm/   (مستقبلي — غير منشأ بعد)
data/implementing_regulations/chinese_internal/    (مستقبلي — غير منشأ بعد)
```

## الترتيب المقترح للاستيعاب المستقبلي

1. استيعاب النص العربي الرسمي للائحة التنفيذية من المصدر الرسمي (أم القرى أو boe.gov.sa)
2. التحقق من المصدر وإثبات المنشأ (source provenance)
3. إنشاء طبقة العربية LLM-ready
4. إضافة الإنجليزية كطبقة مرجعية/إرشادية (اختياري)
5. إضافة الصينية كطبقة مرجعية داخلية (اختياري)

## الحدود

- **اللائحة التنفيذية مسار مستقل** عن النظام (Companies Law corpus)
- **النص العربي الرسمي حاكم**
- **الإنجليزية، إن أُضيفت لاحقًا، مرجعية/إرشادية فقط**
- **الصينية، إن أُضيفت لاحقًا، مرجعية داخلية فقط**
- **ليست رسمية، ليست ملزمة، ليست حاكمة**
- **ليست استشارة قانونية**
- **لا تعديل للنظام أو برنامج المعالجة الصينية المكتمل**