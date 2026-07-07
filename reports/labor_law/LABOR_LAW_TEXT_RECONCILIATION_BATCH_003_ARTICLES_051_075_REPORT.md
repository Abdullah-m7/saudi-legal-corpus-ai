# تقرير تطبيق النصوص الرسمية — الدفعة الثالثة — المواد 51–75 — نظام العمل

## 1. المرحلة والخط الأساسي
- المرحلة: LABOR_LAW_TEXT_RECONCILIATION_BATCH_003_ARTICLES_051_075_WITH_AMENDMENT_POPUP_HANDLING
- الخط الأساسي: cb4a31c326e2c6e0836337798f519deb91a0c465

## 2. الفرع
glm/labor-law-text-reconciliation-batch-003-articles-051-075-popup-aware

## 3. الملفات المنشأة والملفات المعدلة

### ملفات منشأة:
- worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_003_articles_051_075.csv
- reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_003_ARTICLES_051_075_REPORT.md

### ملفات معدلة:
- worksheets/labor_law/reconciliation_scaffold/article_inventory.csv
- worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv
- worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv
- worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv
- worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv

## 4. المصدر المستخدم
المصدر الرسمي المعتمد: الموقع الرسمي للبوابة الإلكترونية لأنظمة المملكة العربية السعودية (BOE)
https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
تاريخ الوصول: 2026-07-07

## 5. منهجية التعامل مع النوافذ المنبثقة للتعديلات
تم تطبيق منهجية التعامل مع النوافذ المنبثقة للتعديلات منذ البداية:
- بالنسبة للمواد غير المعدلة: تم استخراج النص العربي الرسمي من DOM الرئيسي لصفحة BOE فقط.
- بالنسبة للمواد المعدلة: قد يعرض DOM الرئيسي نص المادة الأصلي/الأساسي، بينما تظهر تفاصيل التعديل من خلال نافذة show-amendment المنبثقة. لم يتم توليد نص موحد من النص الأساسي ونافذة التعديل.
- المواد المعدلة التي لم يتم التقاط نصها الرسمي الحالي بشكل آمن تم وضع علامة DO_NOT_INGEST_YET / needs_manual_review.
- لم يتم إجراء أي توحيد أو دمج للنصوص القانونية.

## 6. المواد المشمولة
المواد من 51 إلى 75 (25 مادة).

## 7. عدد صفوف ملف الدفعة
25 صف بيانات + صف الرأس = 26 صف إجمالي.

## 8. عدد المواد التي تمت مصالحتها بنجاح
13 مادة تمت مصالحتها بنجاح من النص العربي الرسمي لـ BOE.

## 9. عدد المواد التي تحتاج إلى مراجعة يدوية
12 مادة تحتاج إلى مراجعة يدوية (11 مادة معدلة + 1 مادة معدلة ومعاد ترقيمها).

## 10. قائمة المواد التي تمت مصالحتها بنجاح
- المادة 56
- المادة 57
- المادة 59
- المادة 60
- المادة 62
- المادة 63
- المادة 65
- المادة 66
- المادة 67
- المادة 68
- المادة 69
- المادة 70
- المادة 71

## 11. قائمة المواد المعدلة/النوافذ المنبثقة/المعاد ترقيمها/التي تحتاج مراجعة
### مواد معدلة (تتطلب مصالحة النافذة المنبثقة):
- المادة 51
- المادة 52
- المادة 53
- المادة 54
- المادة 55
- المادة 61
- المادة 64
- المادة 72
- المادة 73
- المادة 74
- المادة 75

### مادة معدلة ومعاد ترقيمها:
- المادة 58 (تم إعادة ترقيمها بموجب التعديل)

## 12. ملخص مقارنة المرشح المرفوع
لم يتم توفير مرشح مرفوع للمقارنة في هذه المواد (uploaded_candidate_compared_flag=not_available).

## 13. ملخص تحديثات article_inventory.csv
تم تحديث 25 صفاً للمواد 51–75:
- 13 مادة: official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH، reconciliation_status=TEXT_RECONCILED_BATCH_003
- 11 مادة معدلة: official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST
- 1 مادة معدلة ومعاد ترقيمها (58): official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST
- إجمالي صفوف article_inventory.csv لا يزال 247 صف بيانات.

## 14. ملخص تحديثات article_source_checklist.csv
تم تحديث 25 صفاً للمواد 51–75:
- 13 مادة: source_location_status=ARTICLE_TEXT_CAPTURED_FROM_BOE، official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH
- 12 مادة معدلة/معاد ترقيمها: source_location_status=SOURCE_PAGE_IDENTIFIED، official_text_capture_status=NEEDS_MANUAL_CAPTURE
- arabic_source_verified_by_owner_flag=pending_owner_review لجميع المواد.
- إجمالي صفوف article_source_checklist.csv لا يزال 247 صف بيانات.

## 15. ملخص تحديثات extraction_quality_issues.csv
تم إضافة 11 صف جديد للمواد المعدلة 51–75:
- نوع المشكلة: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- حالة الحل: NEEDS_MANUAL_REVIEW
- المادة 58 لها صف سابق (eqi_014) للإعادة الترقيم.
- إجمالي الصفوف: 92 صف بيانات.

## 16. ملخص تحديثات unresolved_issues_log.csv
تم إضافة 12 صف جديد:
- 11 صف للمواد المعدلة (51, 52, 53, 54, 55, 61, 64, 72, 73, 74, 75)
- 1 صف للمادة 58 (المعدلة والمعاد ترقيمها)
- فئة المشكلة: AMENDED_ARTICLE_POPUP_RECONCILIATION
- blocking_flag=no
- owner_decision_needed_flag=yes
- resolution_status=NEEDS_MANUAL_REVIEW
- إجمالي الصفوف: 82 صف بيانات.

## 17. نتيجة readiness_summary
- ingestion_readiness_decision = NOT_READY
- total_unresolved_issues = 82
- ملخص: الدفعة 003 تشمل المواد 51–75؛ 13 مادة تمت مصالحتها بنجاح؛ 12 مادة تحتاج إلى مراجعة يدوية؛ تم تطبيق معالجة النوافذ المنبثقة للتعديلات؛ لم يتم إجراء أي توحيد للنصوص القانونية.

## 18. ما لم يتم فعله عمدًا
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

## 19. تأكيد عدم إجراء إدخال نهائي
لم يتم إجراء أي إدخال نهائي للنظام في المدونة. لا توجد سجلات مدونة نهائية منشأة.

## 20. تأكيد عدم تعديل السجل/التصدير/وقت التشغيل/المدققات
لم يتم إجراء أي تعديلات على registry أو export records أو runtime أو validators.

## 21. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة
لم يتم إنشاء سجلات باللغة الإنجليزية. لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة. السجلات الإنجليزية هي مرجع فقط.

## 22. تأكيد عدم تثبيت ملفات محظورة
لم يتم تثبيت ملفات المصدر أو PDF الرسمية أو HTML الخاص بـ BOE أو ملفات TXT/PDF المرفوعة أو ملفات تفريغ المصدر. لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.

## 23. تأكيد عدم إنشاء نص قانوني موحد
لم يتم توليد أي نص قانوني موحد. لم يتم دمج نص المادة الأساسي مع نص نافذة التعديل المنبثقة.

## 24. نتائج التحقق
تم تشغيل:
- make validate
- make test

## 25. الحدود القانونية والمنتجية
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

## 26. المرحلة التالية الموصى بها
LABOR_LAW_TEXT_RECONCILIATION_BATCH_004_ARTICLES_076_100_WITH_AMENDMENT_POPUP_HANDLING