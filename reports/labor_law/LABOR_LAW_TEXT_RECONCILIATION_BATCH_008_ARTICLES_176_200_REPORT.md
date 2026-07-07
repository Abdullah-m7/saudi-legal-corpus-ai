# تقرير تسوية نصوص نظام العمل — الدفعة 008 (المواد 176–200)

## 1. اسم المرحلة والخط الأساسي

- **المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_008_ARTICLES_176_200_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي:** `3ac08a350a5cc801cdd535547d9693674002f027`

## 2. الفرع

- **اسم الفرع:** `hermes/labor-law-text-reconciliation-batch-008-articles-176-200-popup-aware`

## 3. الملفات المنشأة والمعدلة

### ملفات منشأة:
- `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_008_articles_176_200.csv` (جديد)
- `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_008_ARTICLES_176_200_REPORT.md` (جديد)

### ملفات معدلة:
- `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` (تحديث صفوف 176–200)
- `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv` (تحديث صفوف 176–200)
- `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` (إضافة 6 صفوف جديدة)
- `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` (إضافة 6 قضايا جديدة: issue_099–issue_104)
- `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv` (تحديث العدد الإجمالي)

## 4. المصدر الرسمي المستخدم

المصدر الرسمي المعتمد: الموقع الرسمي للبوابة الوطنية للأنظمة (BOE)
- **الرابط:** `https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1`
- **تاريخ الوصول:** 2026-07-07
- **اللغة الحاكمة:** العربية

## 5. منهجية التعامل مع نوافذ التعديلات (Popup-aware)

تم اتباع قواعد Operator V1 بدقة:
- المقالات غير المعدلة: تم استخراج النص العربي الرسمي من BOE DOM مباشرةً مع حساب SHA-256 وطول الأحرف.
- المقالات المعدلة (changed-article): لم يتم استخراج النص من DOM الرئيسي؛ تُرك حقل النص فارغاً والهاش فارغاً والطول صفراً؛ وُضعت علامة `NEEDS_AMENDMENT_POPUP_RECONCILIATION` و `DO_NOT_INGEST_YET`.
- المقالات الملغاة/المحذوفة: لم يتم التقاط النص القديم/الأساسي كنص رسمي حالي؛ تم نقل القضايا الموجودة دون تكرار.
- المقال المعاد ترقيمه (178): لم يتم اختراع هوية جديدة؛ تم نقل issue_013 الموجود.
- لم يتم توليد أي نص قانوني مدمج من النص الأساسي مع نافذة التعديل.

## 6. المقالات المشمولة

المواد من 176 إلى 200 (25 مادة).

## 7. عدد صفوف الدفعة

- **إجمالي الصفوف:** 25 صف بيانات

## 8. عدد المقالات المسواة نظيفاً

- **16 مقال** مسواة نظيفاً من BOE

## 9. عدد المقالات التي تحتاج مراجعة يدوية

- **9 مقالات** تحتاج مراجعة يدوية (6 معدلة + 1 معاد ترقيمه + 2 ملغاة)

## 10. قائمة المقالات النظيفة المسواة

المواد: 176، 177، 179، 180، 181، 183، 184، 185، 187، 188، 189، 190، 191، 192، 193، 200

## 11. قائمة المقالات المعدلة/المنبثقة/المكررة/الملغاة/المعاد ترقيمها/المراجعة اليدوية

- **مقالات معدلة (تحتاج تسوية نافذة التعديل):** 182، 186، 194، 196، 198، 199
- **مقال معاد ترقيمه ومعدل:** 178
- **مقالات ملغاة/محذوفة:** 195، 197

## 12. ملاحظات التعامل الخاص لكل مقال مشكل

| المقال | الحالة | التعامل |
|--------|--------|---------|
| 178 | معاد ترقيمه ومعدل (M/44) | النص فارغ، الطول 0، `RENUMBERED_ENTRY_NEEDS_MANUAL_RECONCILIATION`، نقل issue_013 الموجود |
| 182 | معدل (M/44) | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_099 جديدة |
| 186 | معدل | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_100 جديدة |
| 194 | معدل | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_101 جديدة |
| 195 | ملغاة (M/44) | النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_018 الموجود |
| 196 | معدل (M/44) | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_102 جديدة |
| 197 | ملغاة (M/44) | النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_019 الموجود |
| 198 | معدل (M/44) | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_103 جديدة |
| 199 | معدل (M/44) | النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_104 جديدة |

## 13. ملخص مقارنة المرشح المرفوع

لم يتم إجراء مقارنة مع مرشح مرفوع في هذه الدفعة. حقل `uploaded_candidate_compared_flag` = `not_available` لجميع الصفوف.

## 14. ملخص تحديث article_inventory.csv

تم تحديث 25 صفاً للمواد 176–200:
- 16 صف: `OFFICIAL_TEXT_CAPTURED_BATCH` / `TEXT_RECONCILED_BATCH_008` / `no` unresolved
- 6 صفوف: `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `needs_manual_check`
- 1 صف (178): `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `needs_manual_check` (renumbered)
- 2 صفوف (195، 197): `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `needs_manual_check` (deleted)

## 15. ملخص تحديث article_source_checklist.csv

تم تحديث 25 صفاً:
- 16 صف: `ARTICLE_TEXT_CAPTURED_FROM_BOE` / `OFFICIAL_TEXT_CAPTURED_BATCH`
- 9 صفوف: `SOURCE_PAGE_IDENTIFIED` / `NEEDS_MANUAL_CAPTURE`

## 16. ملخص تحديث extraction_quality_issues.csv

تمت إضافة 6 صفوف جديدة:
- `eq_batch008_art182` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `eq_batch008_art186` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `eq_batch008_art194` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `eq_batch008_art196` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `eq_batch008_art198` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION
- `eq_batch008_art199` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION

## 17. ملخص تحديث unresolved_issues_log.csv

- **العدد السابق:** 98 قضية غير محلولة
- **قضايا جديدة:** 6 قضايا (issue_099 إلى issue_104)
  - issue_099: المادة 182 معدلة (M/44)
  - issue_100: المادة 186 معدلة
  - issue_101: المادة 194 معدلة
  - issue_102: المادة 196 معدلة (M/44)
  - issue_103: المادة 198 معدلة (M/44)
  - issue_104: المادة 199 معدلة (M/44)
- **قضايا منقولة دون تكرار:** issue_013 (المادة 178)، issue_018 (المادة 195)، issue_019 (المادة 197)
- **العدد الحالي:** 104 قضية غير محلولة

## 18. نتيجة readiness_summary.csv

- **total_unresolved_issues:** 104
- **ingestion_readiness_decision:** NOT_READY

## 19. التحقق الصريح من العدد غير المحلول

- **العدد السابق (قبل الدفعة 008):** 98
- **العدد الحالي لصفوف unresolved_issues_log.csv:** 104
- **العدد الحالي في readiness_summary.csv:** 104
- **التغير:** زيادة بمقدار 6 (من 98 إلى 104)
- **تأكيد:** لم يحدث انخفاض؛ الزيادة بسبب 6 قضايا جديدة للمقالات المعدلة؛ لا توجد إغلاقات موثقة.

## 20. ما لم يتم فعله عمداً

- لم يتم توليد نص قانوني مدمج من النص الأساسي زائد نافذة التعديل.
- لم يتم استخراج نصوص المقالات المعدلة من DOM الرئيسي.
- لم يتم التقاط نصوص المقالات الملغاة كنصوص رسمية حالية.
- لم يتم إجراء مقارنة مع مرشح مرفوع.
- لم يتم إجراء تسوية ثنائية/ثلاثية اللغة.
- لم يتم إنشاء سجلات إنجليزية.
- لم يتم إنشاء سجلات نهائية للقانون.
- لم يتم تعديل Operator V1 أو الفاحص.
- لم يتم تعديل ملفات قانون الشركات.

## 21. تأكيد عدم حدوث إدخال نهائي

لم يحدث أي إدخال نهائي (ingestion) للنصوص في القانون. جميع المقالات النظيفة معلمة `yes` للاستعداد المستقبلي ولكن لم يتم إدخالها في أي سجل نهائي.

## 22. تأكيد عدم تغيير registry/export/runtime/validator

لم يتم تعديل أي ملف في:
- السجل (registry)
- التصدير (export)
- وقت التشغيل (runtime)
- المدققات (validators)

## 23. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة ثنائية/ثلاثية

لم يتم إنشاء أي سجلات إنجليزية. لم يتم إجراء محاذاة ثنائية اللغة أو ثلاثية اللغة. الإنجليزية مرجع مساعد فقط.

## 24. تأكيد عدم وجود ملفات ممنوعة

لم يتم تضمين أي من:
- ملفات HTML أو PDF أو TXT مصدرية من BOE
- ملفات JSON أو JSONL أو XLSX
- ملفات source dumps
- ملفات RAG/UI/API/network/embeddings/LLM

## 25. تأكيد عدم توليد نص قانوني مدمج

لم يتم توليد أي نص قانوني مدمج من النص الأساسي مع نافذة التعديل. جميع المقالات المعدلة تُركت فارغة مع علامة `DO_NOT_INGEST_YET`.

## 26. نتائج التحقق الفعلية

### py_compile
```
python -m py_compile tools/check_labor_law_reconciliation_batch.py
```
النتيجة: نجاح (لا أخطاء ترجمة).

### الفاحص البنيوي
```
python tools/check_labor_law_reconciliation_batch.py --batch 008 --range 176-200 --unresolved-floor 98
```
النتيجة: نجاح — جميع الفحوصات البنيوية مرت (هيكل CSV، عد الصفوف، النصوص الفارغة للمقالات المعدلة/الملغاة، تطابق العدد غير المحلول).

### make validate
```
make validate
```
النتيجة: PASS — ALL CHECKS PASSED ✓

### make test
```
make test
```
النتيجة: 14 failed, 2483 passed. جميع حالات الفشل الـ 14 هي من الفشل المعروف في الحدود الأساسية (chinese_remediation و test_generator). لم يتم إدخال أي فشل جديد. تم التحقق بأن جميع الفشل يقع ضمن فئتي chinese_remediation و test_generator فقط. تم استعادة ملفات البيانات الصينية المعدلة أثناء الاختبار باستخدام `git checkout -- data/ reports/chinese_translation_review/`.

## 27. الحدود القانونية والمنتجية

- المصدر العربي الرسمي من BOE هو الحاكم.
- الإنجليزية مرجع مساعد فقط.
- الصينية مرجع داخلي فقط.
- لا استشارة قانونية.
- لا ترجمة رسمية.
- لا تفسير قانوني.
- لا حكم على الصحة القانونية.
- لا تحقق دلالي.
- لا إدخال نهائي.
- لا تغيير في registry/export/runtime/validators.
- لا سجلات إنجليزية أو محاذاة ثنائية/ثلاثية.
- لا RAG/LLM/API/network/embeddings/UI.

repository-owner legal review active; external legal review optional for enterprise/official adoption

## 28. المرحلة التالية الموصى بها

`LABOR_LAW_TEXT_RECONCILIATION_BATCH_009_ARTICLES_201_225_WITH_AMENDMENT_POPUP_HANDLING`