# تقرير تطبيق نصوص نظام العمل — الدفعة السادسة (المواد 126–150)

## 1. اسم المرحلة والخط الأساسي
- **المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_006_ARTICLES_126_150_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي:** fbab121f536493cf72d229684fc68e61278aa847

## 2. الفرع
- **الفرع:** glm/labor-law-text-reconciliation-batch-006-articles-126-150-popup-aware

## 3. الملفات المنشأة والمعدلة

### الملفات المنشأة:
1. `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_006_articles_126_150.csv`
2. `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_006_ARTICLES_126_150_REPORT.md`

### الملفات المعدلة:
1. `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv`
2. `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv`
3. `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv`
4. `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv`
5. `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv`

## 4. المصدر المستخدم
- المصدر الرسمي العربي: https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- تاريخ الوصول: 2026-07-07
- المصدر العربي الرسمي هو الحاكم.

## 5. منهجية معالجة النوافذ المنبثقة (Popup-aware)
- تم استخراج نصوص المواد من الحاوية الرئيسية `div.HTMLContainer` مع استبعاد الحاويات المنبثقة `div.article_item_popup`.
- بالنسبة للمواد المعدلة: نص DOM الرئيسي قد يكون النص الأصلي/الأساسي، والتعديل يظهر عبر النافذة المنبثقة فقط.
- لم يتم توليد أو دمج أي نص قانوني مُجمَّع من النص الأساسي مع النافذة المنبثقة.
- المواد المعدلة وُضعت تحت DO_NOT_INGEST_YET مع تفريغ حقول النص.

## 6. المواد المشمولة
- المواد 126 حتى 150 (25 مادة).
- لا يوجد صف مكرر مستقل في هذا النطاق (المادة 131 مكرر غير موجودة كعنصر BOE مستقل).

## 7. عدد صفوف الدفعة
- 25 صفًا في ملف الدفعة CSV.

## 8. عدد المواد المُصالَحة بشكل نظيف
- 21 مادة.

## 9. عدد المواد التي تحتاج مراجعة يدوية
- 4 مواد (131، 137، 149، 150).

## 10. قائمة المواد المُصالَحة بشكل نظيف
- 126، 127، 128، 129، 130، 132، 133، 134، 135، 136، 138، 139، 140، 141، 142، 143، 144، 145، 146، 147، 148.

## 11. قائمة المواد المعدلة/المنبثقة/المكرر/الملغاة/المعاد ترقيمها/المراجعة اليدوية
| المادة | السبب |
|--------|-------|
| 131 | مادة معدلة (مكرر مضاف بتعديل M/5)؛ مكرر غير مستقل؛ DOM قد يكون نصًا أساسيًا |
| 137 | مادة معدلة (amended_article_flag)؛ DOM قد يكون نصًا أساسيًا |
| 149 | مادة ملغاة بحكم تعديل (article_deleted_by_amendment)؛ DOM قد يحتوي على نص أساسي |
| 150 | مادة ملغاة بحكم تعديل (article_deleted_by_amendment)؛ DOM قد يحتوي على نص أساسي |

## 12. معالجة المادة 131 مكرر
- المادة 131 مكرر غير موجودة كعنصر BOE مستقل (مؤكد في mukarrar_deleted_renumbered_tracking.csv).
- تتبع التعديلات يؤكد أن مكرر أُضيف بتعديل M/5 (mukarrar_added_by_amendment).
- المشكلة غير المحلولة القائمة (issue_002) محفوظة ولم يتم تكرارها.
- المادة 131 نفسها معدلة أيضًا وتم تعليمها DO_NOT_INGEST_YET مع issue_092 جديدة.

## 13. معالجة المادتين 149 و 150
- المادتان 149 و 150 ملغاتان بحكم تعديل (article_deleted_by_amendment via M/5).
- المشكلات غير المحلولة القائمة (issue_015، issue_016) محفوظة ولم يتم تكرارها.
- لم يتم التقاط النص الأساسي/القديم كنص رسمي حالي.
- تم تعليمها DO_NOT_INGEST_YET مع ready_for_future_ingestion_flag=needs_manual_review.

## 14. ملخص مقارنة المرشح المرفوع
- ملف المرشح (nizam_alamal.txt) غير متاح محليًا.
- تم تعيين uploaded_candidate_compared_flag=not_available.
- لم تتم أي مقارنة. المصدر العربي الرسمي هو الحاكم.

## 15. ملخص تحديثات article_inventory.csv
- 25 صفًا مشمولًا تم تحديثه.
- 21 مادة نظيفة: official_text_capture_status=OFFICIAL_TEXT_CAPTURED_BATCH، reconciliation_status=TEXT_RECONCILED_BATCH_006.
- 4 مواد تحتاج مراجعة: official_text_capture_status=NEEDS_MANUAL_CAPTURE، reconciliation_status=DO_NOT_INGEST.
- إجمالي الصفوف: 247 (لم يتغير).

## 16. ملخص تحديثات article_source_checklist.csv
- 25 صفًا مشمولًا تم تحديثه.
- 21 مادة نظيفة: source_location_status=ARTICLE_TEXT_CAPTURED_FROM_BOE.
- 4 مواد تحتاج مراجعة: source_location_status=SOURCE_PAGE_IDENTIFIED.
- arabic_source_verified_by_owner_flag=pending_owner_review للمواد النظيفة والمعدلة، no للمواد الملغاة.
- إجمالي الصفوف: 247 (لم يتغير).

## 17. ملخص تحديثات extraction_quality_issues.csv
- صفان جديدان أُضيفا:
  - eq_batch006_art131: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
  - eq_batch006_art137: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- صفوف 149 و 150 القائمة (eqi_017، eqi_018) محفوظة ولم تتكرر.
- إجمالي الصفوف: 104 (كان 102، +2).

## 18. ملخص تحديثات unresolved_issues_log.csv
- صفان جديدان أُضيفا:
  - issue_092: labor_law_art_131 | AMENDED_ARTICLE_POPUP_RECONCILIATION
  - issue_093: labor_law_art_137 | AMENDED_ARTICLE_POPUP_RECONCILIATION
- المشكلات القائمة للمواد 149 (issue_015) و 150 (issue_016) محفوظة ولم تتكرر.
- المشكلة القائمة للمادة 131 مكرر (issue_002) محفوظة ولم تتكرر.
- إجمالي الصفوف: 93 (كان 91، +2).

## 19. نتيجة readiness_summary.csv
- total_unresolved_issues = 93
- ingestion_readiness_decision = NOT_READY
- total_articles = 247
- total_amended_articles = 106
- total_m44_related_articles = 45
- total_mukarrar_articles = 2
- total_deleted_or_abolished_articles = 30
- total_renumbered_articles = 5

## 20. التحقق من عدد المشكلات غير المحلولة
- العدد السابق total_unresolved_issues = 91
- العدد الحالي unresolved_issues_log.csv صفوف البيانات = 93
- العدد الحالي readiness_summary total_unresolved_issues = 93
- العدد زاد من 91 إلى 93 (+2 مشكلتان جديدتان: issue_092، issue_093)
- لم ينخفض العدد عن 91. ✓

## 21. ما لم يتم عن قصد
- لم يتم استيعاب نظام العمل في السجل النهائي للمدونة.
- لم يتم إنشاء سجلات نهائية للمواد.
- لم يتم إنشاء سجلات إنجليزية.
- لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة.
- لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF.
- لم يتم توليد نص قانوني مُجمَّع من النص الأساسي مع النافذة المنبثقة.
- لم يتم نسخ نص إنجليزي.
- لم يتم تفسير أو نصائح قانونية.

## 22. تأكيد عدم حدوث استيعاب نهائي
- لم يتم أي استيعاب نهائي لنظام العمل في السجل أو التصدير أو وقت التشغيل. ✓

## 23. تأكيد عدم تغيير السجل/التصدير/وقت التشغيل/المدققات
- لم يتم تعديل registry أو export records أو runtime أو validators. ✓

## 24. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة
- لم يتم إنشاء سجلات إنجليزية. لا توجد محاذاة ثنائية أو ثلاثية اللغة. ✓

## 25. تأكيد عدمcommit ملفات محظورة
- لم يتمcommit ملفات مصدر أو PDF أو HTML أو TXT مرفوعة أو source dumps. ✓

## 26. تأكيد عدم توليد نص قانوني مُجمَّع
- لم يتم توليد أو دمج أي نص قانوني مُجمَّع من النص الأساسي مع النافذة المنبثقة. ✓

## 27. نتائج التحقق
- make validate: PASS — ALL CHECKS PASSED ✓
- make test: 9 failed, 2488 passed
- جميع الفشل التسعة هي فشل قائم مسبقًا في chinese_remediation baseline failures.
- لا فشل جديد تم إدخاله.
- تمت استعادة ملفات البيانات الصينية بعد تشغيل الاختبار.

## 28. الحدود القانونية والمنتجية
- المصدر العربي الرسمي هو الحاكم.
- هذا ليس استشارة قانونية.
- هذا ليس ترجمة رسمية.
- لا تفسير قانوني.
- لا استنتاجات قانونية مولدة.
- لا حكم على الصحة القانونية.
- السجلات الإنجليزية هي مرجعية فقط.
- الترجمة الإنجليزية الرسمية هي دعم مرجعي فقط.
- السجلات الصينية هي مرجع داخلي فقط.
- لا محاذاة ثلاثية اللغة.
- لا ادعاء إصدار عام.
- لا RAG/LLM/API/network/embeddings/UI.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 29. المرحلة التالية الموصى بها
- LABOR_LAW_TEXT_RECONCILIATION_BATCH_007_ARTICLES_151_175_WITH_AMENDMENT_POPUP_HANDLING