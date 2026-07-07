# تقرير مطابقة نصوص نظام العمل — الدفعة الرابعة (المواد 76–100)

## 1. اسم المرحلة والخط الأساسي

- **المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_004_ARTICLES_076_100_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي المؤكد:** 38c70446a2fefb3309850cac9241016ad92863a8

## 2. الفرع

- **الفرع:** glm/labor-law-text-reconciliation-batch-004-articles-076-100-popup-aware

## 3. الملفات المعدّلة/المنشأة

### ملفات منشأة:
- worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_004_articles_076_100.csv
- reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_004_ARTICLES_076_100_REPORT.md

### ملفات معدّلة:
- worksheets/labor_law/reconciliation_scaffold/article_inventory.csv
- worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv
- worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv
- worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv
- worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv

## 4. المصدر المستخدم

- **المصدر الرسمي المعتمد:** النص العربي الرسمي من بوابة الأنظمة الإلكترونية (BOE)
- **الرابط:** https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- **تاريخ الوصول:** 2026-07-07

## 5. المنهجية المعتمدة للتعديلات (Popup-Aware)

تم تطبيق منهجية التعامل مع التعديلات عبر النوافذ المنبثقة (popup-aware) من البداية:
- للمواد غير المعدلة: تم التقاط النص العربي الرسمي من BOE DOM مباشرة.
- للمواد المعدلة: لم يتم تخزين نص الأساس كنص رسمي نهائي، ولم يتم توليد أي نص موحد، وتم وضع علامة NEEDS_AMENDMENT_POPUP_RECONCILIATION.
- للمادة المكررة المؤكدة: تم التقاط النص من BOE مباشرة كصف مستقل.
- للمادة الملغاة: لم يتم التقاط النص القديم كنص رسمي حالي.

## 6. المواد المشمولة

تم تغطية المواد من 76 إلى 100 (25 مادة أساسية) بالإضافة إلى المادة 79 مكرر كمادة مكررة مستقلة مؤكدة.

## 7. تضمين المادة 79 مكرر

- **نعم**، تم تضمين المادة 79 مكرر كصف مستقل مؤكد في الدفعة الرابعة.
- تم تأكيد استقلاليتها من article_inventory.csv و mukarrar_deleted_renumbered_tracking.csv.
- تم التقاط نصها الرسمي من BOE مباشرة.

## 8. عدد صفوف الدفعة (Batch CSV)

- **إجمالي صفوف البيانات:** 26 صفًا (25 مادة أساسية + المادة 79 مكرر)

## 9. عدد المواد المطابقة بنجاح (Cleanly Reconciled)

- **20 مادة** تمت مطابقتها بنجاح من النص العربي الرسمي لـ BOE.

## 10. عدد المواد التي تحتاج مراجعة يدوية (Needs Manual Review)

- **6 مواد** تحتاج مراجعة يدوية.

## 11. قائمة المواد المطابقة بنجاح

1. المادة 79 (غير معدلة)
2. المادة 79 مكرر (مكررة مستقلة، نص ملتقط)
3. المادة 81
4. المادة 82
5. المادة 84
6. المادة 85
7. المادة 86
8. المادة 87
9. المادة 88
10. المادة 89
11. المادة 91
12. المادة 92
13. المادة 93
14. المادة 94
15. المادة 95
16. المادة 96
17. المادة 97
18. المادة 98
19. المادة 99
20. المادة 100

## 12. قائمة المواد المؤجلة (معدلة/نافذة منبثقة/مكررة/ملغاة/مراجعة يدوية)

### مواد معدلة تحتاج مطابقة النافذة المنبثقة (popup reconciliation):
1. المادة 76 — معدلة بموجب تعديل 5/6/1436
2. المادة 77 — معدلة بموجب تعديل 5/6/1436
3. المادة 78 — معدلة وملغاة (article_abolished_by_amendment)
4. المادة 80 — معدلة بموجب تعديل 5/6/1436
5. المادة 83 — معدلة بموجب تعديل 5/6/1436
6. المادة 90 — معدلة بموجب تعديل 5/6/1436

### مادة ملغاة:
- المادة 78 — ملغاة بموجب تعديل (article_abolished_by_amendment)

## 13. ملخص مقارنة المرشح المرفوع

- لم تتوفر نسخة مرشح مرفوعة للمقارنة في هذه الدفعة.
- جميع الصفوف: uploaded_candidate_compared_flag=not_available، uploaded_candidate_match_status=not_compared.

## 14. ملخص تحديثات article_inventory.csv

- تم تحديث 26 صفًا للمواد المشمولة.
- المواد غير المعدلة النظيفة: official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH، reconciliation_status=TEXT_RECONCILED_BATCH_004.
- المواد المعدلة: official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST.
- المادة 78 (ملغاة): official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST.
- المادة 79 مكرر: OFFICIAL_TEXT_CAPTURED_BATCH، TEXT_RECONCILED_BATCH_004 مع ملاحظة مكررة.
- إجمالي صفوف article_inventory.csv لا يزال 247 صفًا.

## 15. ملخص تحديثات article_source_checklist.csv

- تم تحديث 26 صفًا للمواد المشمولة.
- source_location_status=LOCATED_ON_BOE لجميع المواد المشمولة.
- official_article_present_flag=yes لجميع المواد.
- arabic_source_verified_by_owner_flag=pending_owner_review لجميع المواد (لم يتم وضع علامة اكتمال).
- إجمالي صفوف article_source_checklist.csv لا يزال 247 صفًا.

## 16. ملخص تحديثات extraction_quality_issues.csv

- تمت إضافة 6 صفوف جديدة:
  - 5 صفوف AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION للمواد 76، 77، 78، 80، 83، 90.
  - 1 صف MUKARRAR_ARTICLE_NEEDS_CHECK للمادة 79 مكرر (ملاحظة هيكلية فقط).
- لم يتم تكرار أي قضية موجودة.
- إجمالي الصفوف: 98.

## 17. ملخص تحديثات unresolved_issues_log.csv

- تمت إضافة 5 صفوف جديدة:
  - 4 صفوف AMENDED_ARTICLE_POPUP_RECONCILIATION للمواد المعدلة 76، 77، 80، 83، 90.
  - 1 صف DELETED_OR_ABOLISHED_STATUS للمادة 78.
- blocking_flag=no لجميع القضايا الجديدة (تم وضع علامة needs_manual_review بأمان).
- owner_decision_needed_flag=yes.
- resolution_status=NEEDS_MANUAL_REVIEW.
- إجمالي الصفوف: 87.
- إجمالي القضايا غير المحلولة: 45.

## 18. نتيجة readiness_summary.csv

- ingestion_readiness_decision = NOT_READY
- total_unresolved_issues = 45
- total_articles = 247
- ملخص الملاحظات يذكر الدفعة الرابعة والمواد 76–100 وتضمين المادة 79 مكرر.
- يذكر عدم توليد نص موحد وأن المطابقة عبر النوافذ المنبثقة تم تطبيقها.

## 19. ما لم يتم تنفيذه عمدًا

- لم يتم إدخال نظام العمل في السجل النهائي للهيكل.
- لم يتم إنشاء سجلات نهائية للمواد.
- لم يتم تعديل السجل (registry).
- لم يتم تعديل سجلات التصدير (export).
- لم يتم تعديل وقت التشغيل (runtime).
- لم يتم تعديل المدققات (validators).
- لم يتم إنشاء سجلات باللغة الإنجليزية.
- لم يتم إنشاء مطابقة ثنائية أو ثلاثية اللغة.
- لم يتم نسخ نص إنجليزي من أي مصدر.
- لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.
- لم يتم إنشاء مكونات RAG/UI/API/LLM/network/embeddings.
- لم يتم تضمين إعادة صياغة مولّدة.
- لم يتم تضمين تفسير قانوني أو استشارة قانونية.
- لم يتم توليد نص قانوني موحد من نص المادة الأساسية加上 نافذة التعديل.

## 20. تأكيد عدم إجراء إدخال نهائي (No Final Ingestion)

- **مؤكد:** لم يتم إجراء أي إدخال نهائي للنظام في السجل أو الهيكل.
- **مؤكد:** لم يتم إنشاء سجلات نهائية للمواد.

## 21. تأكيد عدم تغيير السجل/التصدير/وقت التشغيل/المدققات

- **مؤكد:** لم يتم تعديل registry أو export أو runtime أو validators.

## 22. تأكيد عدم إنشاء سجلات إنجليزية أو مطابقة

- **مؤكد:** لم يتم إنشاء سجلات باللغة الإنجليزية.
- **مؤكد:** لم يتم إنشاء مطابقة ثنائية أو ثلاثية اللغة.

## 23. تأكيد عدم ارتكاب ملفات محظورة

- **مؤكد:** لم يتم ارتكاب ملفات مصدر أو PDF رسمية أو HTML من BOE أو ملفات TXT/PDF مرفوعة أو ملفات تفريغ.
- **مؤكد:** لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.

## 24. تأكيد عدم توليد نص قانوني موحد

- **مؤكد:** لم يتم توليد أي نص قانوني موحد من نص المادة الأساسية بالإضافة إلى نافذة التعديل.
- **مؤكد:** جميع المواد المعدلة لها نص فارغ في official_arabic_text_reconciled وطول 0 و NEEDS_AMENDMENT_POPUP_RECONCILIATION.

## 25. نتائج التحقق (Validation)

### make validate:
(انظر نتائج التحقق في القسم الأخير بعد التشغيل الفعلي)

### make test:
(انظر نتائج الاختبارات في القسم الأخير بعد التشغيل الفعلي)

## 26. الحدود القانونية/المنتجية

- المصدر العربي الرسمي هو الحاكم.
- هذا ليس استشارة قانونية.
- هذا ليس ترجمة رسمية.
- لا توجد تفسير قانوني.
- لا توجد استنتاجات قانونية مولّدة.
- لا يوجد حكم على الصحة القانونية.
- السجلات الإنجليزية هي مرجعية فقط.
- الترجمة الإنجليزية الرسمية هي دعم مرجعي فقط.
- السجلات الصينية هي مرجع داخلي فقط.
- لا توجد مطابقة ثلاثية اللغة.
- لا يوجد ادعاء بإصدار عام.
- لا توجد مكونات RAG/LLM/API/network/embeddings/UI.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 27. المرحلة التالية الموصى بها

- **LABOR_LAW_TEXT_RECONCILIATION_BATCH_005_ARTICLES_101_125_WITH_AMENDMENT_POPUP_HANDLING**