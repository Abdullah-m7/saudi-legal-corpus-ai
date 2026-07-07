# تقرير تطابق نصوص نظام العمل — الدفعة الخامسة (المواد 101–125)

## 1. اسم المرحلة والخط الأساسي

- **اسم المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_005_ARTICLES_101_125_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي المؤكد:** 1f836dd89bf5a728706d1aa1b109cc6aed71f2e6

## 2. الفرع

- **الفرع:** glm/labor-law-text-reconciliation-batch-005-articles-101-125-popup-aware

## 3. الملفات المعدلة/المنشأة

### ملفات منشأة:
1. `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_005_articles_101_125.csv`
2. `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_005_ARTICLES_101_125_REPORT.md`

### ملفات معدلة:
1. `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv`
2. `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv`
3. `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv`
4. `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv`
5. `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv`

## 4. المصدر المستخدم

- **المصدر الرسمي:** https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- **تاريخ الوصول:** 2026-07-07
- **اللغة الحاكمة:** العربية (المصدر الرسمي العربي يحكم)

## 5. طريقة معالجة النوافذ المنبثقة (Popup-aware method)

تم تطبيق معالجة النوافذ المنبثقة للتعديلات من البداية:
- بالنسبة للمواد غير المعدلة: تم التقاط النص العربي الرسمي من BOE DOM مباشرة.
- بالنسبة للمواد المعدلة (101، 107، 113، 115): تم التحقق من أن BOE قد يعرض النص الأصلي/الأساسي في DOM الرئيسي، بينما تظهر تفاصيل التعديل من خلال نافذة show-amendment المنبثقة. لم يتم تخزين نص DOM الأساسي كنص رسمي مطابق، ولم يتم توليد نص قانوني موحد. تم وضع علامة `NEEDS_AMENDMENT_POPUP_RECONCILIATION` و `DO_NOT_INGEST_YET`.

## 6. المواد المغطاة

المواد 101–125 (25 مادة).

## 7. عدد صفوف الدفعة

25 صفًا (بمعدل صف واحد لكل مادة في النطاق).

## 8. عدد المواد المطابقة بشكل نظيف

21 مادة.

## 9. عدد المواد التي تحتاج مراجعة يدوية

4 مواد.

## 10. قائمة المواد المطابقة بشكل نظيف

المواد: 102، 103، 104، 105، 106، 108، 109، 110، 111، 112، 114، 116، 117، 118، 119، 120، 121، 122، 123، 124، 125

## 11. قائمة المواد المعدلة/المنبثقة/مكرر/ملغاة/معاد ترقيمها/تحتاج مراجعة يدوية

| رقم المادة | الحالة | السبب |
|---|---|---|
| 101 | معدلة — تحتاج مراجعة | BOE main DOM may be base text; amendment shown through popup (M/46) |
| 107 | معدلة — تحتاج مراجعة | BOE main DOM may be base text; amendment shown through popup (M/44 + M/46) |
| 113 | معدلة — تحتاج مراجعة | BOE main DOM may be base text; amendment shown through popup (M/46 + M/44) |
| 115 | معدلة — تحتاج مراجعة | BOE main DOM may be base text; amendment shown through popup (M/46) |

ملاحظة: لا توجد مواد مكرر أو ملغاة أو معاد ترقيمها في نطاق 101–125.

## 12. ملخص مقارنة المرشح المرفوع

- `uploaded_candidate_compared_flag`: not_available (لم يتوفر مرشح مرفوع للمقارنة في هذه الدفعة)
- `uploaded_candidate_match_status`: not_compared
- `uploaded_candidate_issue_type`: not_compared

## 13. ملخص تحديثات article_inventory.csv

- إجمالي الصفوف قبل وبعد التحديث: 247 صفًا (لم يتغير العدد)
- المواد غير المعدلة (21 مادة): `official_text_capture_status` = OFFICIAL_TEXT_CAPTURED_BATCH، `reconciliation_status` = TEXT_RECONCILED_BATCH_005، `unresolved_issue_flag` = no
- المواد المعدلة (4 مواد): `official_text_capture_status` = NEEDS_MANUAL_CAPTURE، `reconciliation_status` = DO_NOT_INGEST، `unresolved_issue_flag` = yes

## 14. ملخص تحديثات article_source_checklist.csv

- إجمالي الصفوف قبل وبعد التحديث: 247 صفًا (لم يتغير العدد)
- جميع المواد 101–125: `source_location_status` = SOURCE_PAGE_IDENTIFIED، `official_article_present_flag` = yes، `arabic_source_verified_by_owner_flag` = pending_owner_review
- المواد غير المعدلة: `official_text_capture_status` = OFFICIAL_TEXT_CAPTURED_BATCH
- المواد المعدلة: `official_text_capture_status` = NEEDS_MANUAL_CAPTURE

## 15. ملخص تحديثات extraction_quality_issues.csv

- إجمالي الصفوف قبل التحديث: 98
- إجمالي الصفوف بعد التحديث: 102
- تمت إضافة 4 صفوف جديدة للمواد المعدلة (101، 107، 113، 115)
- نوع المشكلة: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `resolution_status`: NEEDS_MANUAL_REVIEW

## 16. ملخص تحديثات unresolved_issues_log.csv

- إجمالي الصفوف قبل التحديث: 87
- إجمالي الصفوف بعد التحديث: 91
- تمت إضافة 4 صفوف جديدة (issue_088 إلى issue_091)
- المعرفات: issue_088 (مادة 101)، issue_089 (مادة 107)، issue_090 (مادة 113)، issue_091 (مادة 115)
- فئة المشكلة: AMENDED_ARTICLE_POPUP_RECONCILIATION
- `blocking_flag`: no
- `owner_decision_needed_flag`: yes
- `resolution_status`: NEEDS_MANUAL_REVIEW

## 17. نتيجة readiness_summary.csv

- `total_unresolved_issues` = 91
- `ingestion_readiness_decision` = NOT_READY
- `summary_notes`: تشمل ذكر الدفعة 005 والمواد 101–125، وعدد المواد المطابقة بشكل نظيف (21) وعدد المواد التي تحتاج مراجعة (4)، ومعالجة النوافذ المنبثقة للتعديلات، وتأكيد عدم توليد نص موحد.

## 18. التحقق من العدد غير المحلول

- **العدد السابق (total_unresolved_issues):** 87
- **العدد الحالي (unresolved_issues_log.csv data rows):** 91
- **العدد الحالي (readiness_summary total_unresolved_issues):** 91
- **النتيجة:** العدد **ازداد** من 87 إلى 91 (+4 صفوف جديدة للمواد المعدلة)
- **العدد لم ينخفض تحت 87:** ✓ مؤكد

## 19. ما لم يتم تنفيذه عمدًا

- لم يتم إدخال نظام العمل في corpus النهائي
- لم يتم إنشاء سجلات مواد نهائية في corpus
- لم يتم تعديل registry
- لم يتم تعديل export records
- لم يتم تعديل runtime
- لم يتم تعديل validators
- لم يتم إنشاء سجلات إنجليزية
- لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة
- لم يتم نسخ نص إنجليزي
- لم يتم توليد نص قانوني موحد من نص المادة الأساسي + نافذة التعديل
- لم يتم إنشاء JSON/JSONL/XLSX/PDF
- لم يتم إضافة RAG/UI/API/LLM/network/embeddings

## 20. تأكيد عدم حدوث إدخال نهائي

✓ لم يتم إدخال أي مادة في corpus النهائي. جميع الأعمال تقتصر على ملفات worksheets.

## 21. تأكيد عدم تعديل registry/export/runtime/validators

✓ لم يتم تعديل أي ملف في registry أو export records أو runtime أو validators.

## 22. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة

✓ لم يتم إنشاء أي سجلات إنجليزية أو محاذاة ثنائية أو ثلاثية اللغة.

## 23. تأكيد عدم التزام بملفات محظورة

✓ لم يتم التزام أي ملفات مصدر أو PDF رسمي أو HTML من BOE أو ملفات TXT/PDF مرفوعة أو source dumps. لم يتم إنشاء JSON/JSONL/XLSX/PDF.

## 24. تأكيد عدم توليد نص قانوني موحد

✓ لم يتم توليد أي نص قانوني موحد من نص المادة الأساسي + نافذة التعديل المنبثقة. المواد المعدلة تم تركها فارغة مع علامة `NEEDS_AMENDMENT_POPUP_RECONCILIATION`.

## 25. نتائج التحقق

- `make validate`: PASS
- `make test`: لا فشل جديد يتجاوز الفشل الأساسي المعروف (14 فشل أساسي معروف: 9 chinese_remediation + 5 test_generator_is_byte_stable)

## 26. الحدود القانونية والمنتجية

- المصدر العربي الرسمي يحكم.
- لا يمثل نصيحة قانونية.
- لا يمثل ترجمة رسمية.
- لا يوجد تفسير قانوني.
- لا يوجد استنتاج قانوني مولد.
- لا يوجد حكم على الصحة القانونية.
- السجلات الإنجليزية مرجعية فقط.
- الترجمة الإنجليزية الرسمية دعم مرجعي فقط.
- السجلات الصينية مرجع داخلي فقط.
- لا توجد محاذاة ثلاثية اللغة.
- لا يوجد ادعاء إصدار عام.
- لا RAG/LLM/API/network/embeddings/UI.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 27. المرحلة الموصى بها التالية

LABOR_LAW_TEXT_RECONCILIATION_BATCH_006_ARTICLES_126_150_WITH_AMENDMENT_POPUP_HANDLING