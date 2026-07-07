# تقرير تدقيق إكمال ورقة عمل مصالحة قانون العمل بعد الدفعة 010

- **اسم المرحلة:** LABOR_LAW_RECONCILIATION_WORKSHEET_COMPLETION_AUDIT_AFTER_BATCH_010
- **SHA الأساس:** c7885d6db82d00505ecec1dfa04328f5e13abb81
- **الفرع:** hermes/labor-law-worksheet-completion-audit-after-batch-010
- **نوع المرحلة:** تدقيق فقط (report-only) — لا استيعاب نهائي، لا تعديل ملفات CSV، لا تعديل أدوات أو مدققات

---

## 1. نطاق التدقيق

تدقيق حالة ورقة عمل مصالحة قانون العمل بعد الانتهاء من دفعات المصالحة 001–010 للمواد 1–247. يشمل التدقيق:

- تغطية مخزون المواد (article_inventory.csv)
- تغطية الدفعات (Batches 001–010)
- مجاميع الحالات النظيفة/اليدوية
- سلامة سجل القضايا غير المحلولة (unresolved_issues_log.csv)
- سلامة قضايا جودة الاستخراج (extraction_quality_issues.csv)
- تدقيق الحدود (boundary audit)
- تدقيق التحقق (validation audit)

---

## 2. الملفات المفحوصة

| الملف | المسار |
|------|--------|
| مخزون المواد | `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` |
| قائمة المصادر | `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv` |
| سجل القضايا غير المحلولة | `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` |
| قضايا جودة الاستخراج | `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` |
| ملخص الجاهزية | `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv` |
| الدفعة 001 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_001_articles_001_025.csv` |
| الدفعة 002 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_002_articles_026_050.csv` |
| الدفعة 003 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_003_articles_051_075.csv` |
| الدفعة 004 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_004_articles_076_100.csv` |
| الدفعة 005 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_005_articles_101_125.csv` |
| الدفعة 006 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_006_articles_126_150.csv` |
| الدفعة 007 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_007_articles_151_175.csv` |
| الدفعة 008 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_008_articles_176_200.csv` |
| الدفعة 009 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_009_articles_201_225.csv` |
| الدفعة 010 | `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_010_articles_226_247.csv` |
| أداة التدقيق | `tools/check_labor_law_reconciliation_batch.py` |
| تقرير الدفعة 010 | `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_010_ARTICLES_226_247_REPORT.md` |

## 3. الملفات المنشأة

| الملف | المسار |
|------|--------|
| هذا التقرير | `reports/labor_law/LABOR_LAW_RECONCILIATION_WORKSHEET_COMPLETION_AUDIT_AFTER_BATCH_010_REPORT.md` |

## 4. تأكيد: هذه مرحلة تدقيق فقط (report-only)

- لم يتم إنشاء سجلات قانونية نهائية.
- لم يتم إنشاء نص قانوني موحد من النص الأساسي ونوافذ التعديل.
- لم يتم إنشاء سجلات قانونية باللغة الإنجليزية.
- لم يتم إنشاء سجلات محاذاة ثنائية/ثلاثية اللغة.
- لم يتم تعديل ملفات السجل أو التصدير أو وقت التشغيل أو المدققات.
- لم يتم تعديل ملفات قانون الشركات (Companies Law).
- لم يتم تعديل أي ملف CSV من ملفات الدفعات أو المخزون أو المصادر أو القضايا أو جودة الاستخراج أو ملخص الجاهزية.
- لم يتم إنشاء ملفات مصدر HTML/PDF أو مصنوفات JSON/JSONL/XLSX/PDF.

---

## 5. ملخص مخزون دفعات CSV

| الدفعة | الملف | نطاق المواد | عدد الصفوف |
|-------|------|------------|------------|
| Batch 001 | `labor_law_text_reconciliation_batch_001_articles_001_025.csv` | 1–25 | 25 |
| Batch 002 | `labor_law_text_reconciliation_batch_002_articles_026_050.csv` | 26–50 | 25 |
| Batch 003 | `labor_law_text_reconciliation_batch_003_articles_051_075.csv` | 51–75 | 25 |
| Batch 004 | `labor_law_text_reconciliation_batch_004_articles_076_100.csv` | 76–100 | 26 |
| Batch 005 | `labor_law_text_reconciliation_batch_005_articles_101_125.csv` | 101–125 | 25 |
| Batch 006 | `labor_law_text_reconciliation_batch_006_articles_126_150.csv` | 126–150 | 25 |
| Batch 007 | `labor_law_text_reconciliation_batch_007_articles_151_175.csv` | 151–175 | 25 |
| Batch 008 | `labor_law_text_reconciliation_batch_008_articles_176_200.csv` | 176–200 | 25 |
| Batch 009 | `labor_law_text_reconciliation_batch_009_articles_201_225.csv` | 201–225 | 25 |
| Batch 010 | `labor_law_text_reconciliation_batch_010_articles_226_247.csv` | 226–247 | 21 |
| **المجموع** | | | **247** |

---

## 6. تغطية مخزون المواد

### 6.1 إجمالي صفوف مخزون المواد

- **article_inventory.csv إجمالي صفوف البيانات:** 247 صفًا
- **article_inventory.csv إجمالي article_key فريدة:** 247 مفتاحًا
- **article_inventory.csv إجمالي article_number_current فريدة:** 245 قيمة فريدة

التفسير: `article_number_current` يحتوي على 245 قيمة فريدة بدلاً من 247 لأن:
- المادة 231 تظهر مرتين: مرة كـ `231` (عادية) ومرة كـ `231` (معاد ترقيمها) لكن بمفتاح مختلف (`labor_law_art_231` و `labor_law_art_231_renumbered`)
- المادة 232 تظهر مرتين بنفس النمط (`labor_law_art_232` و `labor_law_art_232_renumbered`)

هذه التكرارات في `article_number_current` مقصودة ومبررة: كل صف له `article_key` فريد يمثل كيانًا قانونيًا مختلفًا (مادة عادية مقابل مادة معاد ترقيمها).

### 6.2 إجمالي total_articles في readiness_summary.csv

- **readiness_summary.csv total_articles:** 247

### 6.3 تغطية ورقة العمل

- **هل تغطي ورقة العمل الحالية جميع صفوف المخزون البالغ 247؟** نعم — إجمالي صفوف الدفعات (247) يساوي إجمالي صفوف المخزون (247).

### 6.4 صفوف المخزون خارج الدفعات 001–010

- **عدد صفوف article_inventory خارج الدفعات 001–010:** 0 (صفر)
- جميع صفوف المخزون الـ 247 مغطاة بالدفعات 001–010.

### 6.5 صفوف الدفعات تشير إلى مواد غير موجودة في المخزون

- **عدد صفوف الدفعات التي تشير إلى article IDs غير موجودة في article_inventory.csv:** 0 (صفر)

---

## 7. تحليل التكرارات

### 7.1 تكرارات عبر الدفعات (cross-batch duplicates)

- **عدد المواد المكررة عبر دفعات مختلفة:** 0 (صفر)
- لا توجد أي مادة تظهر في أكثر من دفعة واحدة.

### 7.2 تكرارات داخل الدفعة 010 (within-batch duplicates)

- المادة 231: تظهر مرتين داخل الدفعة 010 — **مقصود ومبرر**
  - الصف الأول: `article_key = labor_law_art_231`، `mukarrar_or_renumbered_or_deleted_flag = ""` (مادة معدّلة عادية)
  - الصف الثاني: `article_key = labor_law_art_231_renumbered`، `mukarrar_or_renumbered_or_deleted_flag = "renumbered"` (مادة معاد ترقيمها)
- المادة 232: تظهر مرتين داخل الدفعة 010 — **مقصود ومبرر**
  - الصف الأول: `article_key = labor_law_art_232`، `mukarrar_or_renumbered_or_deleted_flag = ""` (مادة معدّلة عادية)
  - الصف الثاني: `article_key = labor_law_art_232_renumbered`، `mukarrar_or_renumbered_or_deleted_flag = "renumbered"` (مادة معاد ترقيمها)

هذه التكرارات في `article_number_current` مقصودة لأن كل صف يمثل كيانًا قانونيًا مختلفًا بمفتاح `article_key` فريد. لا يوجد تكرار حقيقي للصفوف.

---

## 8. تحليل تباين العدد المتوقع للدفعة 010

### 8.1 الوقائع

- **توقع الـ prompt الأصلي:** 22 مادة للنطاق 226–247
- **صفوف الدفعة الفعلية:** 21 صفًا
- **الفرق:** صف واحد (1)

### 8.2 التفسير

المواد 240 و242 و246 و247 غير موجودة في:
- `article_inventory.csv` (لا توجد صفوف لهذه الأرقام)
- BOE (المرجع الرسمي)

التفسير هو أن قانون العمل الحالي لا يحتوي على مواد مرقمة بهذه الأرقام. النطاق 226–247 يحتوي فعليًا على 21 مادة فقط (بما في ذلك `229_mukarrar` وصفي `231` و `232` المعاد ترقيمهما).

### 8.3 التصنيف

هذا **ملاحظة تدقيق (audit note)** وليس خطأً هيكليًا يتطلب تصحيحًا فوريًا. أداة التدقيق `check_labor_law_reconciliation_batch.py` قبلت الدفعة بـ `--expected-rows 21` بنجاح. ومع ذلك، قد يحتاج الـ manifest المستقبلي إلى تحديث لتعكس النطاق الفعلي بدلاً من النطاق الرقمي المتسلسل.

### 8.4 التوصية

- يُسجَّل هذا كملاحظة تدقيق للمراحل المستقبلية.
- لا يلزم تصحيح فوري لأن الأداة قبلت الحالة الحالية والصفوف الإجمالية متسقة (247 = 247).
- إذا تم إنشاء manifest مستقبلي للدفعات، يجب أن يشير إلى أن النطاق 226–247 يحتوي فعليًا على 21 مادة وليس 22.

---

## 9. مجاميع الحالات النظيفة/اليدوية

### 9.1 من article_inventory.csv

| الحالة (reconciliation_status) | العدد |
|-------------------------------|-------|
| TEXT_RECONCILED_BATCH_001 | 13 |
| TEXT_RECONCILED_BATCH_004 | 20 |
| TEXT_RECONCILED_BATCH_005 | 21 |
| TEXT_RECONCILED_BATCH_006 | 21 |
| TEXT_RECONCILED_BATCH_007 | 19 |
| TEXT_RECONCILED_BATCH_008 | 16 |
| TEXT_RECONCILED_BATCH_009 | 3 |
| RECONCILED_FROM_BOE_OFFICIAL_AR | 7 |
| **إجمالي نظيف/مصالَح** | **120** |
| DO_NOT_INGEST | 63 |
| DO_NOT_INGEST_YET | 14 |
| needs_manual_check | 26 |
| no | 24 |
| **إجمالي يدوي/محظور** | **127** |

### 9.2 من ملفات الدفعات (Batch CSVs)

| الحالة (reconciliation_status) | العدد |
|-------------------------------|-------|
| RECONCILED_FROM_BOE_OFFICIAL_AR | 144 |
| DO_NOT_INGEST_YET | 102 |
| NEEDS_MANUAL_REVIEW | 1 |
| **الإجمالي** | **247** |

### 9.3 من ready_for_future_ingestion_flag عبر الدفعات

| القيمة | العدد |
|-------|-------|
| yes | 144 |
| needs_manual_review | 103 |

### 9.4 ملخص الجاهزية

- **ingestion_readiness_decision:** `NOT_READY`
- **total_unresolved_issues:** 114
- **total_amended_articles:** 106
- **total_m44_related_articles:** 45
- **total_mukarrar_articles:** 2
- **total_deleted_or_abolished_articles:** 30
- **total_renumbered_articles:** 5

---

## 10. التحقق من readiness_summary

| الحقل | القيمة في readiness_summary.csv | التحقق |
|------|--------------------------------|--------|
| total_articles | 247 | متطابق مع article_inventory.csv (247 صف) ✓ |
| total_unresolved_issues | 114 | متطابق مع unresolved_issues_log.csv (114 صف) ✓ |
| ingestion_readiness_decision | NOT_READY | لم يتم تغييره ✓ |
| total_amended_articles | 106 | — |
| total_m44_related_articles | 45 | — |
| total_mukarrar_articles | 2 | — |
| total_deleted_or_abolished_articles | 30 | — |
| total_renumbered_articles | 5 | — |

**لم يتم تغيير readiness_summary.csv.** ingestion_readiness_decision يبقى NOT_READY.

---

## 11. التحقق من unresolved_issues_log.csv

| المؤشر | القيمة |
|--------|-------|
| إجمالي صفوف البيانات | 114 |
| أول issue_id | issue_001 |
| آخر issue_id | issue_114 |
| تكرارات issue_id | 0 (لا توجد تكرارات) |
| فجوات في التسلسل الرقمي | لا توجد (1–114 متسلسل بالكامل) |
| article_keys فارغة | 6 صفوف (issue_001, issue_002, issue_003, issue_004, issue_007, issue_008) — جميعها قضايا هيكلية/تتبع وليست مرتبطة بمادة معينة |
| مقالات لها أكثر من قضية | 5 مقالات |
| — labor_law_art_002 | 3 قضايا (issue_009, issue_010, issue_044) — كل قضية بفئة مختلفة |
| — labor_law_art_035 | قضيتان (issue_011, issue_070) — إعادة ترقيم + تعديل popup |
| — labor_law_art_058 | قضيتان (issue_012, issue_082) — إعادة ترقيم + تعديل popup |
| — labor_law_art_011 | قضيتان (issue_045, issue_049) — تصحيح نصي + تعديل popup |
| — (فارغ) | 6 قضايا هيكلية |

### تأكيد: القضايا المحمولة (carried-forward) لم تكرر

القضايا من الدفعات السابقة (مثل issue_041, issue_042, issue_043 للمواد 226–228) تبقى كما هي ولم تكرر في الدفعة 010. القضايا الجديدة issue_106 إلى issue_114 أضيفت للمواد المعدّلة في النطاق 226–247.

### آخر issue_id بعد الدفعة 010

- **issue_114** (مرتبط بـ labor_law_art_241 — AMENDED_ARTICLE_POPUP_RECONCILIATION)

### القضايا الجديدة للدفعة 010

| issue_id | article_key | الفئة |
|----------|-------------|------|
| issue_106 | labor_law_art_229 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_107 | labor_law_art_230 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_108 | labor_law_art_231 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_109 | labor_law_art_232 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_110 | labor_law_art_236 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_111 | labor_law_art_237 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_112 | labor_law_art_238 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_113 | labor_law_art_239 | AMENDED_ARTICLE_POPUP_RECONCILIATION |
| issue_114 | labor_law_art_241 | AMENDED_ARTICLE_POPUP_RECONCILIATION |

---

## 12. التحقق من extraction_quality_issues.csv

| المؤشر | القيمة |
|--------|-------|
| إجمالي صفوف البيانات | 125 |
| تكرارات issue_id | 0 (لا توجد تكرارات) |

### توزيع بادئات المعرّفات

| البادئة | العدد |
|---------|-------|
| eqi_ | 60 |
| issue_ | 47 |
| eq_batch | 18 |

### إضافات الدفعة 010 (eqi_52 إلى eqi_60)

| issue_id | article_key | النوع |
|----------|-------------|------|
| eqi_52 | labor_law_art_229 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_53 | labor_law_art_230 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_54 | labor_law_art_231 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_55 | labor_law_art_232 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_56 | labor_law_art_236 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_57 | labor_law_art_237 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_58 | labor_law_art_238 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_59 | labor_law_art_239 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |
| eqi_60 | labor_law_art_241 | AMENDED_ARTICLE_BOE_POPUP_REQUIRES_RECONCILIATION |

**ملاحظة تنسيق:** معرّفات eqi_52 إلى eqi_60 تستخدم تنسيقًا مختلفًا (`eqi_52` بدون حشو صفر) مقارنةً بالمعرّفات الأقدم (`eqi_001` إلى `eqi_051` بحشو صفر). هذا اختلاف تنسيق بادئي غير مؤثر (cosmetic formatting inconsistency) ولا يؤثر على التفرد أو السلامة الهيكلية.

### اتساق إضافات unresolved_issues_log و extraction_quality_issues للدفعة 010

- 9 مقالات معدّلة (Articles 229, 230, 231, 232, 236, 237, 238, 239, 241) تم توثيقها في كل من:
  - `unresolved_issues_log.csv` (issue_106 إلى issue_114)
  - `extraction_quality_issues.csv` (eqi_52 إلى eqi_60)
- **النتيجة:** متسقة ومتوافقة ✓

---

## 13. تدقيق الحدود (Boundary Audit)

تم التحقق مما يلي وكلها **مؤكدة سلبية** (لم تحدث):

| الحد | النتيجة |
|-----|--------|
| استيعاب نهائي (final ingestion) | لم يحدث ✓ |
| إنشاء نص قانوني موحد من النص الأساسي + نافذة التعديل | لم يحدث ✓ |
| سجلات قانونية بالإنجليزية | لم يتم إنشاؤها ✓ |
| سجلات محاذاة ثنائية/ثلاثية اللغة | لم يتم إنشاؤها ✓ |
| تغييرات في registry/export/runtime/validators | لم تحدث ✓ |
| تغييرات في RAG/UI/API/LLM/network/embeddings | لم تحدث ✓ |
| ملفات BOE HTML/PDF/source dumps | لم يتم إنشاؤها ✓ |
| مصنوفات JSON/JSONL/XLSX/PDF | لم يتم إنشاؤها ✓ |
| تغييرات في ملفات قانون الشركات (Companies Law) | لم تحدث ✓ |
| تعديل Operator V1 | لم يحدث ✓ |
| تعديل checker | لم يحدث ✓ |
| تعديل ملفات CSV (الدفعات، المخزون، المصادر، القضايا، جودة الاستخراج، ملخص الجاهزية) | لم يحدث ✓ |

### فحص الملفات المحظورة في worksheets/labor_law/

- لم يتم العثور على أي ملفات بامتداد `.json` أو `.jsonl` أو `.xlsx` أو `.pdf` أو `.html` في `worksheets/labor_law/`.

---

## 14. نتائج التحقق الفعلية (Validation Audit)

### 14.1 py_compile

**الأمر:** `python -m py_compile tools/check_labor_law_reconciliation_batch.py`

**النتيجة:** نجح بدون أخطاء (exit_code = 0، لا مخرجات)

### 14.2 make validate

**الأمر:** `make validate`

**النتيجة:**
```
============================================================
Saudi Companies Law — Book 1 corpus validation
============================================================
[PASS] schema
------------------------------------------------------------
RESULT: ALL CHECKS PASSED ✓
```

### 14.3 make test

**الأمر:** `make test`

**النتيجة:** 14 فشل، 2483 نجح (25.80 ثانية)

**تصنيف الفشل:**

جميع الفشل الـ 14 هي **فشل خط أساس معروف (known baseline failures)** في اختبارات الترجمة الصينية لقانون الشركات. لا توجد فشل مرتبطة بقانون العمل.

قائمة الاختبارات الفاشلة:
1. `test_chinese_all_babs_source_inventory.py::test_generator_is_byte_stable`
2. `test_chinese_internal_legal_llm_isolable_source_articles.py::test_chinese_text_exact_and_hash`
3. `test_chinese_internal_legal_llm_isolable_source_articles.py::test_generator_is_byte_stable`
4. `test_chinese_internal_llm_semantic_qa_gap_plan.py::test_generator_is_byte_stable`
5. `test_chinese_remediation_backlog_source_packet_plan.py::test_generator_is_byte_stable`
6. `test_chinese_remediation_batch_p1_003.py::test_validator_passes_on_current_outputs`
7. `test_chinese_remediation_batch_p1_003.py::test_prior_candidate_link_matches_unchanged_candidate`
8. `test_chinese_remediation_batch_p1_003_qa.py::test_validator_passes_on_current_outputs`
9. `test_chinese_remediation_batch_p2_002.py::test_validator_passes_on_current_outputs`
10. `test_chinese_remediation_batch_p2_002.py::test_prior_candidate_link_matches_unchanged_candidate`
11. `test_chinese_remediation_batch_p2_002_qa.py::test_validator_passes_on_current_outputs`
12. `test_chinese_remediation_batch_p2_003.py::test_validator_passes_on_current_outputs`
13. `test_chinese_remediation_batch_p2_003.py::test_prior_candidate_link_matches_unchanged_candidate`
14. `test_chinese_remediation_batch_p2_003_qa.py::test_validator_passes_on_current_outputs`

**ملاحظة:** `make test` أدى إلى تشغيل مولدات أدت إلى تغيير محتوى بعض ملفات JSON المولّدة (byte-stability drift). تمت استعادة جميع الملفات المتأثرة إلى حالتها الأصلية باستخدام `git checkout -- .`. تم التحقق من نظافة حالة git بعد الاستعادة (`git status --short` = فارغ).

**لم يتم العثور على فشل جديد (new failures).**

### 14.4 تشغيل المدقق للدفعة 010

**الأمر:** `python tools/check_labor_law_reconciliation_batch.py --batch 010 --range 226-247 --unresolved-floor 105 --expected-rows 21`

**النتيجة:**
```
PASS: batch CSV structure OK: .../labor_law_text_reconciliation_batch_010_articles_226_247.csv
PASS: readiness/unresolved counts OK
PASS: report structure and boundary wording OK
PASS: Labor Law reconciliation batch structural check completed
```

**exit_code = 0** — نجح بالكامل.

---

## 15. تأكيدات صريحة

- **لم يحدث استيعاب نهائي (no final ingestion occurred).**
- **ingestion_readiness_decision يبقى NOT_READY.**

---

## 16. فئات المخاطر/الاستثناءات المتبقية

### 16.1 مخاطر غير حاجبة (non-blocking risks)

1. **مقالات معدّلة معلّقة (amended articles with popup reconciliation needed):** 106 مادة معدّلة تحتاج معالجة يدوية لدمج النص الأساسي مع نص نافذة التعديل قبل الاستيعاب. موثّقة في `unresolved_issues_log.csv` (114 قضية) و `extraction_quality_issues.csv`.

2. **مقالات محذوفة/ملغاة:** 30 مادة محذوفة/ملغاة موثّقة بـ `DO_NOT_INGEST` — لا تحتاج استيعابًا.

3. **مقالات معاد ترقيمها:** 5 مواد معاد ترقيمها تحتاج معالجة يدوية لتأكيد الترقيم الحالي.

4. **مقالات مكررة (mukarrar):** مادتان مكررتان (11 مكرر و 131 مكرر) تحتاجان تحققًا يدويًا.

5. **اختلاف تنسيق معرّفات eqi:** معرّفات `eqi_52` إلى `eqi_60` تستخدم تنسيقًا بدون حشو صفر، بينما المعرّفات الأقدم تستخدم حشو صفر (`eqi_001`). اختلاف تجميلي غير مؤثر.

6. **تباين العدد المتوقع للدفعة 010:** المواد 240 و242 و246 و247 غير موجودة في المخزون ولا في BOE. هذا ملاحظة تدقيق وليس خطأً هيكليًا.

### 16.2 مخاطر حاجبة (blocking risks)

لا توجد مخاطر حاجبة هيكلية. جميع الفشل في `make test` هي فشل خط أساس معروف في اختبارات قانون الشركات الصينية ولا علاقة لها بقانون العمل.

---

## 17. المرحلة الموصى بها التالية

بناءً على نتائج التدقيق:

- **تغطية الورقة:** مكتملة (247/247)
- **التكرارات:** مبررة وموثّقة (لا توجد تكرارات حقيقية)
- **الفجوات:** لا توجد (0 صفوف خارج الدفعات)
- **القضايا غير المحلولة:** 114 قضية — جميعها موثّقة ومتسقة
- **السلامة الهيكلية:** سليمة
- **الفشل في الاختبارات:** جميعها فشل خط أساس معروف (لا فشل جديد)

**المرحلة الموصى بها:**

**LABOR_LAW_AMENDMENT_POPUP_REMEDIATION_STRATEGY_AFTER_WORKSHEET_COMPLETION**

تغطية الورقة مكتملة والقضايا المتبقية هي قضايا تعديل popup والمقالات المحذوفة/المعاد ترقيمها التي تحتاج استراتيجية معالجة وليست تناقضات هيكلية.

**لا تبدأ المرحلة التالية.**

---

## 18. ملخص نتائج التدقيق

| المؤشر | القيمة |
|--------|-------|
| التغطية | **مكتملة** (complete) |
| إجمالي صفوف article_inventory | 247 |
| إجمالي صفوف الدفعات 001–010 | 247 |
| التكرارات الحقيقية | 0 (التكرارات في article_number_current مقصودة ومبررة) |
| الفجوات | 0 (لا توجد صفوف خارج الدفعات) |
| readiness_summary total_unresolved_issues | 114 |
| unresolved_issues_log row count | 114 |
| extraction_quality_issues row count | 125 |
| py_compile | PASS |
| make validate | PASS (ALL CHECKS PASSED ✓) |
| make test | 14 فشل (جميعها فشل خط أساس معروف)، 2483 نجح |
| checker batch 010 | PASS (exit_code = 0) |
| استيعاب نهائي | لم يحدث |
| ingestion_readiness_decision | NOT_READY (لم يتغير) |
| المرحلة التالية الموصى بها | LABOR_LAW_AMENDMENT_POPUP_REMEDIATION_STRATEGY_AFTER_WORKSHEET_COMPLETION |