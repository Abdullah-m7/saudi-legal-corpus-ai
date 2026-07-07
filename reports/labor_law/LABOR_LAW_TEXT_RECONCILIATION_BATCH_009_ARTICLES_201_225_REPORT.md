# تقرير تسوية نصوص نظام العمل — الدفعة 009 (المواد 201–225)

## 1. اسم المرحلة والخط الأساسي

- **المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_009_ARTICLES_201_225_WITH_AMENDMENT_POPUP_HANDLING
- **الخط الأساسي:** `fa7f1b5364dc1cfe9305045f2d54239f18643da4`

## 2. الفرع

- **اسم الفرع:** `hermes/labor-law-text-reconciliation-batch-009-articles-201-225-popup-aware`

## 3. الملفات المنشأة والمعدلة

### ملفات منشأة:
- `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_009_articles_201_225.csv` (جديد)
- `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_009_ARTICLES_201_225_REPORT.md` (جديد)

### ملفات معدلة:
- `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` (تحديث صفوف 201–225)
- `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv` (تحديث صفوف 201–225)
- `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` (إضافة 1 صف جديد)
- `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` (إضافة 1 قضية جديدة: issue_105)
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
- لم يتم توليد أي نص قانوني مدمج من النص الأساسي مع نافذة التعديل.

### المحاولة الموثقة لكل مقال معدل/منبثق:

**المادة 209 (معدلة بمرسوم م/44):**
1. تم فتح صفحة BOE الرسمية لنظام العمل.
2. تم تحديد عنصر المادة 209 في DOM؛ وعليه صنف `changed-article`.
3. هيكل BOE يعرض النص الأساسي القديم في DOM الرئيسي مع نافذة تعديل (popup) تحتوي على النص المعدل المقتبس بعد عبارة «وعدلت هذه المادة لتكون بالنص الآتي».
4. النص المعدل موجود داخل نافذة التعديل فقط، وليس معروضاً كنص مقالي رسمي حالي في DOM الرئيسي.
5. بما أن الهيكل هو نص أساسي زائد نافذة تعديل، ووفقاً لقواعد Operator V1، لا يتم توليد نص مدمج.
6. النتيجة: النص الرسمي الحالي بعد التعديل غير قابل للالتقاط الآمن من DOM الرئيسي دون دمج؛ تُرك النص فارغاً والطول صفراً واعتبر `DO_NOT_INGEST_YET` مع `needs_manual_review`.

**المقالات الملغاة/المحذوفة (203، 205–208، 210–225):**
1. تم فتح صفحة BOE الرسمية.
2. هذه المقالات مصنفة كـ `changed-article` في DOM وعليها علامة الإلغاء في ملفات التتبع.
3. لم يتم التقاط النص القديم/الأساسي كنص رسمي حالي.
4. تم نقل القضايا الموجودة (issue_020 إلى issue_040) دون تكرار.

## 6. المقالات المشمولة

المواد من 201 إلى 225 (25 مادة).

## 7. عدد صفوف الدفعة

- **إجمالي الصفوف:** 25 صف بيانات

## 8. عدد المقالات المسواة نظيفاً

- **3 مقالات** مسواة نظيفاً من BOE

## 9. عدد المقالات التي تحتاج مراجعة يدوية

- **22 مقالاً** تحتاج مراجعة يدوية (1 معدلة زائد 21 ملغاة/محذوفة)

## 10. قائمة المقالات النظيفة المسواة

المواد: 201، 202، 204

## 11. قائمة المقالات المعدلة/المنبثقة/المكررة/الملغاة/المعاد ترقيمها/المراجعة اليدوية

- **مقالات معدلة (تحتاج تسوية نافذة التعديل):** 209
- **مقالات ملغاة/محذوفة:** 203، 205، 206، 207، 208، 210، 211، 212، 213، 214، 215، 216، 217، 218، 219، 220، 221، 222، 223، 224، 225

## 12. ملاحظات التعامل الخاص لكل مقال مشكل

### المادة 203 (ملغاة عبر م/44):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_020 الموجود.

### المادة 205 (ملغاة عبر م/44):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_021 الموجود.

### المادة 206 (ملغاة عبر م/44):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_022 الموجود.

### المادة 207 (ملغاة عبر م/44):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_023 الموجود.

### المادة 208 (ملغاة عبر م/44):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_024 الموجود.

### المادة 209 (معدلة عبر م/44):
- النص فارغ، الطول 0، `NEEDS_AMENDMENT_POPUP_RECONCILIATION`، `DO_NOT_INGEST_YET`، issue_105 جديدة.
- السبب: هيكل BOE يعرض نصاً أساسياً في DOM الرئيسي مع نافذة تعديل تحتوي على النص المعدل؛ لا يمكن الالتقاط الآمن دون دمج؛ لم يتم توليد نص مدمج.

### المادة 210 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_025 الموجود.

### المادة 211 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_026 الموجود.

### المادة 212 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_027 الموجود.

### المادة 213 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_028 الموجود.

### المادة 214 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_029 الموجود.

### المادة 215 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_030 الموجود.

### المادة 216 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_031 الموجود.

### المادة 217 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_032 الموجود.

### المادة 218 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_033 الموجود.

### المادة 219 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_034 الموجود.

### المادة 220 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_035 الموجود.

### المادة 221 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_036 الموجود.

### المادة 222 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_037 الموجود.

### المادة 223 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_038 الموجود.

### المادة 224 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_039 الموجود.

### المادة 225 (ملغاة):
- النص فارغ، الطول 0، `DELETED_OR_ABOLISHED_NEEDS_MANUAL_RECONCILIATION`، نقل issue_040 الموجود.

## 13. ملخص مقارنة المرشح المرفوع

لم يتم إجراء مقارنة مع مرشح مرفوع في هذه الدفعة. حقل `uploaded_candidate_compared_flag` = `not_available` لجميع الصفوف.

## 14. ملخص تحديث article_inventory.csv

تم تحديث 25 صفاً للمواد 201–225:
- 3 صفوف: `OFFICIAL_TEXT_CAPTURED_BATCH` / `TEXT_RECONCILED_BATCH_009` / `no` unresolved
- 1 صف (209): `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `needs_manual_check` (amended)
- 21 صفوف (203، 205–208، 210–225): `NEEDS_MANUAL_CAPTURE` / `DO_NOT_INGEST` / `needs_manual_check` (deleted/abolished)

## 15. ملخص تحديث article_source_checklist.csv

تم تحديث 25 صفاً:
- 3 صفوف: `ARTICLE_TEXT_CAPTURED_FROM_BOE` / `OFFICIAL_TEXT_CAPTURED_BATCH`
- 22 صفوف: `SOURCE_PAGE_IDENTIFIED` / `NEEDS_MANUAL_CAPTURE`

## 16. ملخص تحديث extraction_quality_issues.csv

تمت إضافة 1 صف جديد:
- `eq_batch009_art209` — AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION

## 17. ملخص تحديث unresolved_issues_log.csv

- **العدد السابق:** 104 قضية غير محلولة
- **قضايا جديدة:** 1 قضية (issue_105)
  - issue_105: المادة 209 معدلة (م/44)؛ هيكل BOE يعرض نصاً أساسياً مع نافذة تعديل؛ النص الرسمي الحالي غير قابل للالتقاط الآمن
- **قضايا منقولة دون تكرار:** issue_020 (المادة 203)، issue_021 (المادة 205)، issue_022 (المادة 206)، issue_023 (المادة 207)، issue_024 (المادة 208)، issue_025 (المادة 210)، issue_026 (المادة 211)، issue_027 (المادة 212)، issue_028 (المادة 213)، issue_029 (المادة 214)، issue_030 (المادة 215)، issue_031 (المادة 216)، issue_032 (المادة 217)، issue_033 (المادة 218)، issue_034 (المادة 219)، issue_035 (المادة 220)، issue_036 (المادة 221)، issue_037 (المادة 222)، issue_038 (المادة 223)، issue_039 (المادة 224)، issue_040 (المادة 225)
- **العدد الحالي:** 105 قضية غير محلولة

## 18. نتيجة readiness_summary.csv

- **total_unresolved_issues:** 105
- **ingestion_readiness_decision:** NOT_READY

## 19. التحقق الصريح من العدد غير المحلول

- **العدد السابق (قبل الدفعة 009):** 104
- **العدد الحالي لصفوف unresolved_issues_log.csv:** 105
- **العدد الحالي في readiness_summary.csv:** 105
- **التغير:** زيادة بمقدار 1 (من 104 إلى 105)
- **تأكيد:** لم يحدث انخفاض؛ الزيادة بسبب 1 قضية جديدة للمادة 209 المعدلة؛ لا توجد إغلاقات موثقة.

## 20. ما لم يتم فعله عمداً

- لم يتم توليد نص قانوني مدمج من النص الأساسي مع نافذة التعديل.
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
python tools/check_labor_law_reconciliation_batch.py --batch 009 --range 201-225 --unresolved-floor 104
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

`LABOR_LAW_TEXT_RECONCILIATION_BATCH_010_ARTICLES_226_247_WITH_AMENDMENT_POPUP_HANDLING`