# تقرير تطبيق النصوص الرسمية — الدفعة الثانية — المواد 26–50 — نظام العمل

## 1. المرحلة
LABOR_LAW_TEXT_RECONCILIATION_BATCH_002_ARTICLES_026_050_WITH_AMENDMENT_POPUP_HANDLING

## 2. الخط الأساسي (Baseline)
3453335b81a1d4db677df7ed522d172b948d12f4

## 3. الفرع (Branch)
glm/labor-law-text-reconciliation-batch-002-articles-026-050-popup-aware

## 4. الملفات المنشأة والملفات المعدلة

### ملفات منشأة:
- worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_002_articles_026_050.csv
- reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_002_ARTICLES_026_050_REPORT.md

### ملفات معدلة:
- worksheets/labor_law/reconciliation_scaffold/article_inventory.csv
- worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv
- worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv
- worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv
- worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv

## 5. المصدر المستخدم
المصدر الرسمي المعتمد: الموقع الرسمي للبوابة الإلكترونية لأنظمة المملكة العربية السعودية (BOE)
https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1

تاريخ الوصول: 2026-07-07

## 6. منهجية التعامل مع النوافذ المنبثقة للتعديلات (Popup-aware method)
تم تطبيق منهجية التعامل مع النوافذ المنبثقة للتعديلات منذ البداية:
- بالنسبة للمواد غير المعدلة: تم استخراج النص العربي الرسمي من DOM الرئيسي لصفحة BOE فقط.
- بالنسبة للمواد المعدلة: قد يعرض DOM الرئيسي نص المادة الأصلي/الأساسي، بينما تظهر تفاصيل التعديل من خلال نافذة show-amendment المنبثقة. لم يتم توليد نص موحد من النص الأساسي ونافذة التعديل.
- المواد المعدلة التي لم يتم التقاط نصها الرسمي الحالي بشكل آمن تم وضع علامة DO_NOT_INGEST_YET / needs_manual_review.
- لم يتم إجراء أي توحيد أو دمج للنصوص القانونية.

## 7. المواد المشمولة
المواد من 26 إلى 50 (25 مادة).

## 8. عدد صفوف ملف الدفعة
25 صف بيانات + صف الرأس = 26 صف إجمالي.

## 9. عدد المواد التي تمت مصالحتها بنجاح
11 مادة تمت مصالحتها بنجاح من النص العربي الرسمي لـ BOE.

## 10. عدد المواد التي تحتاج إلى مراجعة يدوية
14 مادة تحتاج إلى مراجعة يدوية (13 مادة معدلة + 1 مادة معدلة ومعاد ترقيمها).

## 11. قائمة المواد التي تمت مصالحتها بنجاح
- المادة 26
- المادة 29
- المادة 32
- المادة 33
- المادة 34
- المادة 36
- المادة 38
- المادة 41
- المادة 45
- المادة 49
- المادة 50

## 12. قائمة المواد المعدلة/النوافذ المنبثقة/المحذوفة/المعاد ترقيمها/التي تحتاج مراجعة
### مواد معدلة (تتطلب مصالحة النافذة المنبثقة):
- المادة 27
- المادة 28
- المادة 30
- المادة 31
- المادة 37
- المادة 39
- المادة 40
- المادة 42
- المادة 43
- المادة 44
- المادة 46
- المادة 47
- المادة 48

### مادة معدلة ومعاد ترقيمها:
- المادة 35 (تم إعادة ترقيمها بموجب التعديل عبر م/44)

## 13. ملخص مقارنة المرشح المرفوع
لم يتم توفير مرشح مرفوع للمقارنة في هذه المواد (uploaded_candidate_compared_flag=not_available).

## 14. ملخص تحديثات article_inventory.csv
تم تحديث 25 صفاً للمواد 26–50:
- 11 مادة: official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH، reconciliation_status=TEXT_RECONCILED_BATCH_002
- 13 مادة معدلة: official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST
- 1 مادة معدلة ومعاد ترقيمها (35): official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST
- إجمالي صفوف article_inventory.csv لا يزال 247 صف بيانات.

## 15. ملخص تحديثات article_source_checklist.csv
تم تحديث 25 صفاً للمواد 26–50:
- 11 مادة: source_location_status=ARTICLE_TEXT_CAPTURED_FROM_BOE، official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH
- 14 مادة معدلة: source_location_status=SOURCE_PAGE_IDENTIFIED، official_text_capture_status=NEEDS_MANUAL_CAPTURE
- arabic_source_verified_by_owner_flag=pending_owner_review لجميع المواد (لم يتم تحديد التحقق من قبل المالك كمكتمل).
- إجمالي صفوف article_source_checklist.csv لا يزال 247 صف بيانات.

## 16. ملخص تحديثات extraction_quality_issues.csv
تم إضافة 13 صف جديد (issue_069 إلى issue_081) للمواد المعدلة 27–48:
- نوع المشكلة: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- حالة الحل: NEEDS_MANUAL_REVIEW
- المادة 35 لها صف سابق (eqi_013) للإعادة الترقيم.
- إجمالي الصفوف: 81 صف بيانات.

## 17. ملخص تحديثات unresolved_issues_log.csv
تم إضافة 14 صف جديد (issue_057 إلى issue_070):
- 13 صف للمواد المعدلة (27, 28, 30, 31, 37, 39, 40, 42, 43, 44, 46, 47, 48)
- 1 صف للمادة 35 (المعدلة والمعاد ترقيمها)
- فئة المشكلة: AMENDED_ARTICLE_POPUP_RECONCILIATION
- blocking_flag=no
- owner_decision_needed_flag=yes
- resolution_status=NEEDS_MANUAL_REVIEW
- إجمالي الصفوف: 70 صف بيانات.

## 18. نتيجة readiness_summary
- ingestion_readiness_decision = NOT_READY
- total_unresolved_issues = 70
- ملخص: الدفعة 002 تشمل المواد 26–50؛ 11 مادة تمت مصالحتها بنجاح؛ 14 مادة تحتاج إلى مراجعة يدوية؛ تم تطبيق معالجة النوافذ المنبثقة للتعديلات؛ لم يتم إجراء أي توحيد للنصوص القانونية.

## 19. ما لم يتم فعله عمدًا
- لم يتم إدخال نظام العمل في المدونة النهائية.
- لم يتم إنشاء سجلات المواد النهائية للمدونة.
- لم يتم تعديل السجل (registry).
- لم يتم تعديل سجلات التصدير (export).
- لم يتم تعديل وقت التشغيل (runtime).
- لم يتم تعديل المدققات (validators).
- لم يتم إنشاء سجلات باللغة الإنجليزية.
- لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة.
- لم يتم نسخ النص الإنجليزي.
- لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.
- لم يتم إضافة RAG/UI/API/LLM/network/embeddings.
- لم يتم تضمين إعادة صياغة مولدة.
- لم يتم تضمين تفسير أو استشارة قانونية.
- لم يتم توليد نص قانوني موحد من نص المادة الأساسي بالإضافة إلى نافذة التعديل المنبثقة.

## 20. تأكيد عدم إجراء إدخال نهائي
لم يتم إجراء أي إدخال نهائي للنظام في المدونة. لا توجد سجلات مدونة نهائية منشأة.

## 21. تأكيد عدم تعديل السجل/التصدير/وقت التشغيل/المدققات
لم يتم إجراء أي تعديلات على registry أو export records أو runtime أو validators.

## 22. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة
لم يتم إنشاء سجلات باللغة الإنجليزية. لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة. السجلات الإنجليزية هي مرجع فقط.

## 23. تأكيد عدم تثبيت ملفات محظورة
لم يتم تثبيت ملفات المصدر أو PDF الرسمية أو HTML الخاص بـ BOE أو ملفات TXT/PDF المرفوعة أو ملفات تفريغ المصدر. لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.

## 24. تأكيد عدم إنشاء نص قانوني موحد
لم يتم توليد أي نص قانوني موحد. لم يتم دمج نص المادة الأساسي مع نص نافذة التعديل المنبثقة.

## 25. نتائج التحقيد
تم تشغيل:
- make validate
- make test

## 26. الحدود القانونية والمنتجية
- المصدر العربي الرسمي يحكم.
- هذا ليس استشارة قانونية.
- هذا ليس ترجمة رسمية.
- لا يوجد تفسير قانوني.
- لا توجد استنتاجات قانونية مولدة.
- لا يوجد حكم على الصحة القانونية.
- السجلات الإنجليزية هي مرجع فقط.
- الترجمة الإنجليزية الرسمية هي دعم مرجعي فقط.
- السجلات الصينية هي مرجع داخلي فقط.
- لا توجد محاذاة ثلاثية اللغة.
- لا ادعاء بإصدار عام.
- لا توجد RAG/LLM/API/network/embeddings/UI.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 27. المرحلة التالية الموصى بها
LABOR_LAW_TEXT_RECONCILIATION_BATCH_003_ARTICLES_051_075_WITH_AMENDMENT_POPUP_HANDLING