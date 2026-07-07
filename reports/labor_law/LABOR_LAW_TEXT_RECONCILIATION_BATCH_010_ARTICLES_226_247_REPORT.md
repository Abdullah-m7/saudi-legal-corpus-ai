# تقرير الدفعة 010 لمصالحة نصوص قانون العمل — المواد 226–247

## 1. اسم المرحلة والخط الأساسي

- **اسم المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_010_ARTICLES_226_247_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي (SHA):** 3f0e82030519280ad376e305bada7724b99a17a3
- **الفرع:** hermes/labor-law-text-reconciliation-batch-010-articles-226-247-popup-aware

## 2. الملفات المنشأة والمعدّلة

### ملفات منشأة:
- `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_010_articles_226_247.csv` (الدفعة)
- `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_010_ARTICLES_226_247_REPORT.md` (هذا التقرير)

### ملفات معدّلة:
- `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` (21 صفًا محدّثًا)
- `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv` (21 صفًا محدّثًا)
- `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` (9 صفوف جديدة)
- `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` (9 صفوف جديدة)
- `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv` (صف واحد محدّث)

## 3. المصدر الرسمي المستخدم

- **المصدر:** الموقع الرسمي للبوابة القانونية (BOE) — أمين العدل الإلكتروني
- **الرابط:** https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- **تاريخ الوصول:** 2026-07-07
- **طريقة الجلب:** تحميل HTML عبر curl (الصفحة تُعرض بالكامل من الخادم)

## 4. منهجية معالجة نافذة التعديل

تم اتباع القواعد التالية لكل مادة في النطاق 226–247:

1. فتح الصفحة الرسمية BOE وتحديد عنصر المادة في DOM.
2. فحص صنف CSS للعنصر — إذا كان يحتوي على `changed-article` فهو مادة معدّلة.
3. للمواد غير المعدّلة: التقاط النص الرسمي من DOM مباشرة.
4. للمواد المعدّلة (changed-article): لم يتم التقاط النص الأساسي لأنه لا يمثل النص الحالي بعد التعديل. تم ترك الحقول فارغة ووضع علامة `needs_manual_review`.
5. للمواد المحذوفة/الملغاة: لم يتم التقاط النص الأساسي كنص حالي. تم تفويضها بقضية موجودة.
6. للمواد المكررة (مضافة بمرسوم): التقاط النص المُقتبس فقط (بين علامتي التنصيص) بعد إزالة سطر المرجع للمرسوم.
7. للمواد المعاد ترقيمها: تفويض القضية الموجودة من دفعة سابقة.
8. لم يتم إنشاء أي نص قانوني مُجمّع من النص الأساسي مع نافذة التعديل.

## 5. محاولة موثّقة لكل مادة معدّلة أو يدوية

### المواد المحذوفة/الملغاة (3 مواد):

| المادة | الحالة | السبب |
|--------|--------|-------|
| 226 | محذوفة/ملغاة | تم تأكيد الحذف في ملف التتبع — القضية issue_041 محمولة |
| 227 | محذوفة/ملغاة | تم تأكيد الحذف في ملف التتبع — القضية issue_042 محمولة |
| 228 | محذوفة/الملغاة | تم تأكيد الحذف في ملف التتبع — القضية issue_043 محمولة |

### المواد المعدّلة (9 مواد):

| المادة | الحالة | السبب |
|--------|--------|-------|
| 229 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 230 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 231 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 232 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 236 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 237 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 238 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 239 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |
| 241 | NEEDS_AMENDMENT_POPUP_RECONCILIATION | BOE يعرض النص الأساسي مع نافذة تعديل — يمنع الالتقاط الآمن للنص الحالي |

### المواد المعاد ترقيمها (مادتان):

| المادة | الحالة | السبب |
|--------|--------|-------|
| 231_renumbered | RENUMBERED_ENTRY_NEEDS_MANUAL_RECONCILIATION | مادة معاد ترقيمها — القضية issue_005 محمولة من دفعة سابقة |
| 232_renumbered | RENUMBERED_ENTRY_NEEDS_MANUAL_RECONCILIATION | مادة معاد ترقيمها — القضية issue_006 محمولة من دفعة سابقة |

## 6. المواد المشمولة

- **نطاق المواد:** 226–247
- **عدد المواد الفعلية:** 21 صفًا (المواد 240 و242 و246 و247 غير موجودة في المخزون ولا في BOE)

## 7. عدد صفوف الدفعة

- **عدد صفوف الدفعة (Batch CSV):** 21 صفًا
- **عدد المواد المتوقع وفق المخزون:** 21 مادة
- **ملاحظة:** المواد 240 و242 و246 و247 غير موجودة في المخزون (article_inventory.csv) ولا في BOE. المخزون الكلي هو 247 صفًا، والدفعات 001–009 تغطي 226 صفًا، فيتبقى 21 صفًا للدفعة 010. تم استخدام `--expected-rows 21` في فحص البنية.

## 8. عدد المواد المصالحة بنجاح

- **عدد المواد المصالحة بنجاح (Clean):** 7 مواد

## 9. عدد المواد التي تحتاج مراجعة يدوية

- **عدد المواد التي تحتاج مراجعة يدوية (Manual):** 14 مادة

## 10. قائمة المواد المصالحة بنجاح

| # | المادة | المفتاح | طريقة المصدر | طول النص (أحرف) |
|---|--------|---------|--------------|----------------|
| 1 | 229 مكرر | labor_law_art_229_mukarrar | MUKARRAR_ARTICLE_TEXT_CAPTURED | 223 |
| 2 | 233 | labor_law_art_233 | BOE_DOM_ARTICLE_TEXT | 188 |
| 3 | 234 | labor_law_art_234 | BOE_DOM_ARTICLE_TEXT | 292 |
| 4 | 235 | labor_law_art_235 | BOE_DOM_ARTICLE_TEXT | 168 |
| 5 | 243 | labor_law_art_243 | BOE_DOM_ARTICLE_TEXT | 159 |
| 6 | 244 | labor_law_art_244 | BOE_DOM_ARTICLE_TEXT | 214 |
| 7 | 245 | labor_law_art_245 | BOE_DOM_ARTICLE_TEXT | 86 |

## 11. قائمة المواد المعدّلة والمحذوفة والمعاد ترقيمها واليدوية

| # | المادة | المفتاح | التصنيف | سبب التفويض |
|---|--------|---------|---------|-------------|
| 1 | 226 | labor_law_art_226 | محذوفة | DELETED_OR_ABOLISHED |
| 2 | 227 | labor_law_art_227 | محذوفة | DELETED_OR_ABOLISHED |
| 3 | 228 | labor_law_art_228 | محذوفة | DELETED_OR_ABOLISHED |
| 4 | 229 | labor_law_art_229 | معدّلة | AMENDMENT_POPUP |
| 5 | 230 | labor_law_art_230 | معدّلة | AMENDMENT_POPUP |
| 6 | 231 | labor_law_art_231 | معدّلة | AMENDMENT_POPUP |
| 7 | 232 | labor_law_art_232 | معدّلة | AMENDMENT_POPUP |
| 8 | 236 | labor_law_art_236 | معدّلة | AMENDMENT_POPUP |
| 9 | 237 | labor_law_art_237 | معدّلة | AMENDMENT_POPUP |
| 10 | 238 | labor_law_art_238 | معدّلة | AMENDMENT_POPUP |
| 11 | 239 | labor_law_art_239 | معدّلة | AMENDMENT_POPUP |
| 12 | 241 | labor_law_art_241 | معدّلة | AMENDMENT_POPUP |
| 13 | 231_renumbered | labor_law_art_231_renumbered | معاد ترقيمها | RENUMBERED |
| 14 | 232_renumbered | labor_law_art_232_renumbered | معاد ترقيمها | RENUMBERED |

## 12. ملاحظات معالجة خاصة

### المادة 229 مكرر:
- مادة مكررة مضافة بالمرسوم الملكي م/44 وتاريخ 1446/2/8هـ.
- BOE يعرضها كعنصر مستقل غير معدّل (لا يحمل صنف changed-article).
- تم التقاط النص المُقتبس فقط (بين علامتي التنصيص) بعد إزالة سطر المرجع للمرسوم.
- النص الرسمي الحالي ظاهر بوضوح في BOE.

### المواد 233 و234 و235:
- مواد مضافة بمراسيم (م/46 وم/14) — مسجّلة كـ DUPLICATE_BOE_ITEM في ملف التتبع.
- BOE يعرضها كعناصر غير معدّلة (لا تحمل صنف changed-article) مع النص الكامل.
- النص يبدأ بمرجع للمرسوم ثم النص المُقتبس بين علامتي التنصيص.
- تم التقاط النص المُقتبس فقط كنص رسمي حالي.
- النص الرسمي الحالي ظاهر بوضوح في BOE.

### المواد 226 و227 و228:
- مواد محذوفة/ملغاة (من الفصل 14 — فصل فضّ منازعات العمل الذي ألغي بموجب م/44 وم/1).
- تم تأكيد الحذف في ملف التتبع.
- لم يتم التقاط النص الأساسي كنص حالي.
- القضايا issue_041 وissue_042 وissue_043 محمولة من دفعة سابقة.

### المواد المعاد ترقيمها (231_renumbered و232_renumbered):
- مواد معاد ترقيمها — BOE يعرض العنوان بترقيم حالي وسابق.
- القضايا issue_005 وissue_006 محمولة من دفعة سابقة.

## 13. ملخص مقارنة المرشح المرفوع

- لم تتم مقارنة المرشح المرفوع في هذه الدفعة.
- `uploaded_candidate_compared_flag = no` لجميع الصفوف.

## 14. ملخص تحديث article_inventory.csv

- تم تحديث 21 صفًا في article_inventory.csv.
- التحديثات شملت: official_text_capture_status، reconciliation_status، unresolved_issue_flag، reviewer_notes.
- المواد المصالحة: status = RECONCILED_FROM_BOE_OFFICIAL_AR، unresolved_issue_flag = no.
- المواد المحذوفة/المعدّلة/المعاد ترقيمها: status = DO_NOT_INGEST_YET، unresolved_issue_flag = yes.

## 15. ملخص تحديث article_source_checklist.csv

- تم تحديث 21 صفًا في article_source_checklist.csv.
- التحديثات شملت: source_location_status، official_article_present_flag، official_text_capture_status، source_notes.
- جميع المواد: source_location_status = SOURCE_PAGE_IDENTIFIED، official_article_present_flag = yes.

## 16. ملخص تحديث extraction_quality_issues.csv

- تمت إضافة 9 قضايا جديدة (eqi_052 حتى eqi_060) للمواد المعدّلة.
- نوع القضية: AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION.
- حالة الحل: NEEDS_MANUAL_REVIEW.
- القضايا الموجودة سابقًا (eqi_007، eqi_008، eqi_012، eqi_043، eqi_044، eqi_045) محمولة ولم يتم تكرارها.

## 17. ملخص تحديث unresolved_issues_log.csv

- تمت إضافة 9 قضايا جديدة (issue_106 حتى issue_114) للمواد المعدّلة التالية:
  - issue_106: labor_law_art_229 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_107: labor_law_art_230 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_108: labor_law_art_231 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_109: labor_law_art_232 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_110: labor_law_art_236 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_111: labor_law_art_237 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_112: labor_law_art_238 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_113: labor_law_art_239 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
  - issue_114: labor_law_art_241 (AMENDED_ARTICLE_POPUP_RECONCILIATION)
- القضايا الموجودة سابقًا (issue_005، issue_006، issue_041، issue_042، issue_043) محمولة ولم يتم تكرارها.

## 18. نتيجة readiness_summary.csv

- `total_articles = 247`
- `total_amended_articles = 106`
- `total_m44_related_articles = 45`
- `total_mukarrar_articles = 2`
- `total_deleted_or_abolished_articles = 30`
- `total_renumbered_articles = 5`
- `total_unresolved_issues = 114`
- `ingestion_readiness_decision = NOT_READY`

## 19. التحقق الصريح من عدد القضايا غير المحلولة

- **العدد السابق:** 105
- **عدد صفوف unresolved_issues_log.csv الحالي:** 114
- **عدد readiness_summary total_unresolved_issues الحالي:** 114
- **التغيير:** ارتفع من 105 إلى 114 (زيادة 9 قضايا جديدة)
- **التأكيد:** لم يتم إغلاق أي قضية. جميع القضايا الجديدة موثّقة للمواد المعدّلة في النطاق 226–247.
- **تطابق:** unresolved_issues_log.csv (114 صفًا) = readiness_summary total_unresolved_issues (114) ✓

## 20. ما لم يتم عمله عمدًا

- لم يتم إنشاء سجلات قانونية نهائية.
- لم يتم إجراء استيعاب نهائي.
- لم يتم تعديل السجل أو التصدير أو وقت التشغيل أو المدققات.
- لم يتم إنشاء سجلات إنجليزية.
- لم يتم إنشاء محاذاة ثنائية اللغة أو ثلاثية اللغة.
- لم يتم إنشاء نص قانوني مُجمّع من النص الأساسي مع نافذة التعديل.
- لم يتم تقديم نصائح قانونية أو تفسيرات قانونية.
- لم يتم الحكم على الصحة القانونية.
- لم يتم تعديل ملفات قانون الشركات.
- لم يتم الالتقاط النص الأساسي للمواد المحذوفة كنص حالي.

## 21. تأكيد عدم حدوث استيعاب نهائي

- لم يتم إجراء استيعاب نهائي لأي مادة.
- جميع البيانات تظل على مستوى ورقة العمل فقط.

## 22. تأكيد عدم تغيير السجل أو التصدير أو وقت التشغيل أو المدققات

- لم يتم تعديل: السجل (registry)، سجلات التصدير (export records)، وقت التشغيل (runtime)، المدققات (validators).
- لم يتم تعديل ملفات Operator V1 أو أداة الفحص (checker).

## 23. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة ثنائية/ثلاثية اللغة

- لم يتم إنشاء أي سجلات إنجليزية.
- لم يتم إنشاء أي محاذاة ثنائية اللغة أو ثلاثية اللغة.
- الإنجليزية مرجع مساعد فقط. الصينية مرجع داخلي فقط.

## 24. تأكيد عدم ارتكاب ملفات ممنوعة

- لم يتم ارتكاب: ملفات BOE HTML، ملفات JSON، ملفات JSONL، ملفات XLSX، ملفات PDF، ملفات مصدر مرفوعة.
- لم يتم ارتكاب: مكونات RAG/UI/API/LLM/network/embeddings.
- لم يتم ارتكاب: ملفات قانون الشركات.

## 25. تأكيد عدم إنشاء نص قانوني مُجمّع

- لم يتم إنشاء أي نص قانوني مُجمّع من النص الأساسي مع نافذة التعديل.
- للمواد المعدّلة: النص فارغ، الهاش فارغ، الطول صفر.
- للمواد المحذوفة: لم يتم التقاط النص الأساسي كنص حالي.

## 26. نتائج التحقق الفعلية

### py_compile:
```
python -m py_compile tools/check_labor_law_reconciliation_batch.py
```
النتيجة: نجاح (exit code 0) — لا توجد أخطاء بناء.

### فحص البنية (Structural Checker):
```
python tools/check_labor_law_reconciliation_batch.py --batch 010 --range 226-247 --unresolved-floor 105 --expected-rows 21
```
النتيجة: PASS — جميع الفحوصات اجتازت بنجاح (بنية CSV، عدد القضايا، بنية التقرير، الحدود).

### make validate:
```
make validate
```
النتيجة: PASS — ALL CHECKS PASSED ✓

### make test:
```
make test
```
النتيجة: 14 failed, 2483 passed. جميع الإخفاقات في فئتي `chinese_remediation` و`test_generator_is_byte_stable` — وهي إخفاقات أساسية معروفة. لم يتم إدخال أي إخفاقات جديدة. تم استرجاع ملفات البيانات الصينية المعدّلة بعد الاختبار: `git checkout -- data/ reports/chinese_translation_review/`.

## 27. الحدود القانونية والمنتجية

- المصدر العربي الرسمي هو الحاكم.
- الإنجليزية مرجع مساعد فقط.
- الصينية مرجع داخلي فقط.
- لا توجد نصائح قانونية.
- لا توجد ترجمة رسمية.
- لا توجد تفسيرات قانونية.
- لا يوجد حكم على الصحة القانونية.
- لا يوجد استيعاب نهائي.
- لا توجد تغييرات على السجل أو التصدير أو وقت التشغيل أو المدققات.
- لا توجد سجلات إنجليزية أو محاذاة ثنائية/ثلاثية اللغة.
- لا توجد ملفات ممنوعة.
- لا يوجد نص قانوني مُجمّع.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 28. المرحلة التالية الموصى بها

LABOR_LAW_RECONCILIATION_WORKSHEET_COMPLETION_AUDIT_AFTER_BATCH_010