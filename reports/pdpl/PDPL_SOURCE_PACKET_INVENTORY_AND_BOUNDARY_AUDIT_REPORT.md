# تقرير جرد حزمة المصدر وتدقيق الحدود — نظام حماية البيانات الشخصية (PDPL / SDAIA)

---

## المرحلة (Stage)

`PDPL_SOURCE_PACKET_INVENTORY_AND_BOUNDARY_AUDIT`

---

## النتيجة (Result)

تقرير فقط (Report-only) — جرد حزمة مصدر وتدقيق حدود. لا استيعاب. لا إنشاء سجلات JSONL. لا إنشاء مخططات. لا إنشاء مدققات. لا تعديل ملفات قانون العمل أو نظام الشركات. لا تعديل runtime أو API أو RAG أو UI أو embeddings أو مدققات.

---

## مرجع الأساس (Baseline SHA)

- **Base SHA المتوقع:** `4ed0371313cfae2f4d50349d5ff3277aa1c056de`
- **Base SHA الفعلي (origin/main):** `4ed0371313cfae2f4d50349d5ff3277aa1c056de`
- **محلي HEAD:** `4ed0371313cfae2f4d50349d5ff3277aa1c056de`
- **تم التحقق:** ✓ (مطابق)

---

## النطاق (Scope)

جرد وتدقيق حزمة مصدر PDPL/SDAIA المرفقة كملف ZIP، تحتوي على أربعة ملفات PDF:
1. النظام الأساسي — عربي (المصدر الحاكم للنظام)
2. النظام الأساسي — إنجليزي (مرجعي فقط)
3. اللائحة التنفيذية — عربي (المصدر الحاكم للائحة)
4. اللائحة التنفيذية — إنجليزي (مرجعي فقط)

الهدف: تأسيس نظام PDPL كمسار قانوني تالي بعد قانون العمل ونظام الشركات.

---

## معلومات ملف ZIP

- **اسم ملف ZIP:** `PDPL_SDAIA.zip`
- **الحجم (بايت):** 4,911,597
- **SHA-256:** `d9409fba7d63a7fc4b4bd86c3f54da5a066303e7df02461b7839159763c8d9f3`
- **عدد الملفات داخل ZIP:** 4

---

## محتويات ZIP بالضبط

| # | اسم الملف | الامتداد |
|---|-----------|---------|
| 1 | `PDPL_نظام_حماية_البيانات_الشخصية_عربي.pdf` | .pdf |
| 2 | `PDPL_Personal_Data_Protection_Law_English.pdf` | .pdf |
| 3 | `PDPL_اللائحة_التنفيذية_عربي.pdf` | .pdf |
| 4 | `PDPL_Implementing_Regulation_English.pdf` | .pdf |

---

## جدول جرد الملفات (Per-File Inventory)

| الحقل | ملف 1 | ملف 2 | ملف 3 | ملف 4 |
|-------|-------|-------|-------|-------|
| **filename** | PDPL_نظام_حماية_البيانات_الشخصية_عربي.pdf | PDPL_Personal_Data_Protection_Law_English.pdf | PDPL_اللائحة_التنفيذية_عربي.pdf | PDPL_Implementing_Regulation_English.pdf |
| **extension** | .pdf | .pdf | .pdf | .pdf |
| **size_bytes** | 772,297 | 1,558,413 | 1,724,286 | 1,548,907 |
| **sha256** | `0bb6d1eb6a85450af4d4eb74b9e87bd2c8f62abab0eb0474087ffcbdf5e2292c` | `f8e499d3ee1a76085df022a12fbd9f40b56be3034f26b510225c0cb3f73d55af` | `4b4b24e3bcb744a04a39a65d890454fc63ea282be85501af125d5f36134919df` | `fccdb1d9f0f07ab74e6dc5a4dda84c951a43d1a11fe19dd467324617594b2a14` |
| **language** | عربي | إنجليزي | عربي | إنجليزي |
| **source_layer** | PDPL_LAW_ARABIC_GOVERNING_SOURCE | PDPL_LAW_ENGLISH_REFERENCE_ONLY | PDPL_REGULATION_ARABIC_GOVERNING_SOURCE | PDPL_REGULATION_ENGLISH_REFERENCE_ONLY |
| **expected_role** | المصدر الحاكم للنظام | مرجعي فقط | المصدر الحاكم للائحة التنفيذية | مرجعي فقط |
| **page_count** | 16 | 16 | 22 | 27 |
| **encrypted** | لا | لا | لا | لا |
| **text_extractable** | لا (نص مشوّه — ترميز خطوط subset بـ Identity-H بدون ToUnicode CMap؛ 0 حرف عربي قابل للقراءة عبر جميع الصفحات الـ16) | نعم (33,698 حرف مستخرج) | نعم (40,937 حرف مستخرج؛ 20/22 صفحة قابلة للقراءة بنص عربي سليم) | نعم (49,855 حرف مستخرج) |
| **OCR_needed** | نعم — مطلوب OCR كامل قبل جرد المواد | لا | لا | لا |
| **authority_visible** | غير قابل للتحقق من النص المستخرج (نص مشوّه)؛ العنوان في البيانات الوصفية: «نظام حماية البيانات الشخصية ولوايحه التنظيمية ١» | نعم — يشير إلى Competent Authority و Council of Ministers | نعم — يشير إلى هيئة الحكومة الرقمية (Digital Government Authority) | نعم — يشير إلى Royal Decree No. (M/19) و Royal Decree No. (M/148) |
| **date_or_version_visible** | غير قابل للتحقق من النص المستخرج؛ بيانات PDF الوصفية: تاريخ الإنشاء 2025-07-17 | نعم — العنوان الوصفي في البيانات الوصفية: «V2-23April2023-Reviewed» (مرجعي، ليس تاريخ صدور رسمي) | نعم — المرسوم الملكي رقم م/19 بتاريخ 9/2/1443ﻫـ والمعدل بالمرسوم الملكي رقم م/148 بتاريخ 5/9/1444ﻫـ | نعم — Royal Decree No. (M/19) dated 9/2/1443H and amended by Royal Decree No. (M/148) dated 5/9/1444 AH |
| **article_numbering_visible** | غير قابل للتحقق من النص المستخرج (نص مشوّه) | نعم — Article 1 إلى Article 43 (مع غياب Article 30 في التسلسل المرصود؛ 42 مرجع للمواد) | نعم — 82 مرجع للمواد بصيغة «المادة» (أشكال عرضية مختلفة) | نعم — Article 1 إلى Article 38 (54 مرجع للمواد عبر النص) |

---

## قسم حدود المصدر (Source Boundary Section)

### الحدود القانونية للمصدر:

1. **النظام الأساسي (Law):** ملف PDF العربي `PDPL_نظام_حماية_البيانات_الشخصية_عربي.pdf` هو **المصدر الحاكم** لطبقة النظام. أي تعارض بين النص العربي والإنجليزي يُحتجّ بالنص العربي.

2. **اللائحة التنفيذية (Implementing Regulation):** ملف PDF العربي `PDPL_اللائحة_التنفيذية_عربي.pdf` هو **المصدر الحاكم** لطبقة اللائحة التنفيذية. أي تعارض بين النص العربي والإنجليزي يُحتجّ بالنص العربي.

3. **ملفات PDF الإنجليزية:** مرجعية فقط (reference-only). لا تحكم على العربية. لا تُستخدم كنص حاكم في أي طبقة.

4. **عدم الدمج:** النظام واللائحة التنفيذية طبقتان منفصلتان. لا يتم دمجهما في نص قانوني واحد.

5. **لا نصيحة قانونية:** هذا التقرير لا يحتوي على نصيحة قانونية ولا تفسير قانوني.

6. **لا ادعاء ترجمة رسمية:** لا يُدّعى أن ملفات PDF الإنجليزية ترجمة رسمية ما لم ينص المصدر نفسه صراحةً على ذلك. لم يُعثر على إعلان رسمي صريح في الملفات الإنجليزية عن صفة الترجمة الرسمية. العنوان الوصفي للبيانات الوصفية للنظام الإنجليزي هو «Personal Data English V2-23April2023-Reviewed» — وهذا لا يشير صراحةً إلى صفة الترجمة الرسمية.

---

## قسم جودة الاستخراج (Extraction Quality Section)

### ملف 1: PDPL_نظام_حماية_البيانات_الشخصية_عربي.pdf

- **القابلية للاستخراج:** لا — النص المستخرج مشوّه تماماً
- **السبب:** الخطوط المدمجة تستخدم ترميز Identity-H (subset fonts) بدون ToUnicode CMap صالح. تم العثور على 6 خطوط مدمجة على الأقل في الصفحة 1 (ArialMT، HelveticaNeueLTArabic-Roman بمتغيرات متعددة). النص المستخرج يحتوي على رموز ASCII عشوائية بدلاً من نص عربي.
- **عدد الأحرف العربية المستخرجة:** 0 عبر جميع الصفحات الـ16 (1 حرف فقط في صفحة الغلاف = رمز «عام»)
- **إجمالي الأحرف المستخرجة:** 38,720 (نص مشوّه غير قابل للاستخدام)
- **نموذج النص (صفحة 1، أول 500 حرف):**
  ```
  !"#$%&#'( )*+,#!#- )*./0,( !"
  #$%& !'("): !"# $ %&'() *+, ,!-./01 2345 6 7/8!
  9/: ;,!<'/=,> ,?%(@ -A2-B/ ;=C> DE *+, ,!-./0- ,!
  B</FE ,!B'(-@ AG/0 HI G-J/1 G/ !K 24LMN ,!O(/P Q
  (# R!S: 1- ,!-./0: F./0 TB/2@ ,!'(/F/> ,!UV5(@.
  2- ,!WX,YZ: ,!WX,YZ ,!L-9(+2@ !W-./0.
  ```
  **التقييم:** نص مشوّه تماماً — غير قابل للاستخدام لأي جرد على مستوى المواد.
- **OCR مطلوب:** نعم

### ملف 2: PDPL_Personal_Data_Protection_Law_English.pdf

- **القابلية للاستخراج:** نعم — نص إنجليزي سليم
- **إجمالي الأحرف المستخرجة:** 33,698
- **نموذج النص (صفحة 1، أول 500 حرف):**
  ```
  Personal Data Protection Law
  Article 1
  For the purpose of implementing this Law, the following terms shall have the meanings
  assigned thereto, unless the context requires otherwise:
  1-Law: The Personal Data Protection Law.
  2-Regulations: The Implementing Regulations of the Law.
  3-Competent Authority: The authority to be determined by a resolution of the Council of
  Ministers.
  4-Personal Data: Any data, regardless of its source or form, that may lead to identifying an
  individual specifi
  ```
- **نموذج عنوان مادة (Article 1):**
  ```
  Article 1
  For the purpose of implementing this Law, the following terms shall have the meanings
  assigned thereto, unless the context requires otherwise:
  ```
  **التقييم:** استخراج ممتاز — نص سليم وقابل للقراءة.

### ملف 3: PDPL_اللائحة_التنفيذية_عربي.pdf

- **القابلية للاستخراج:** نعم — نص عربي سليم في 20/22 صفحة
- **إجمالي الأحرف المستخرجة:** 40,937
- **عدد الصفحات القابلة للقراءة (أكثر من 50 حرف عربي):** 20 من 22
- **صفحة 0 (غلاف):** نص ضئيل (64 حرف) + صورتان (شعار 199×69 وصورة كبيرة 1836×2376)
- **صفحة 21:** نص ضئيل جداً (5 أحرف)
- **نموذج النص (صفحة 1، أول 500 حرف):**
  ```
  اﻟﺒﻴﺎﻧﺎت ﺣﻤﺎﻳﺔ ﻟﻨﻈﺎم اﻟﺘﻨﻔﻴﺬﻳﺔ اﻟﻼﺋﺤﺔ
  اﻟﺸﺨﺼﻴﺔ
  اﻟﺘﻌﺮﻳﻔﺎت :اﻷوﻟﻰ اﻟﻤﺎدة
  ﺗﻜﻮن ﻟﻠﻜﻠﻤﺎت واﻟﻌﺒﺎرات اﻟﻮاردة ﻓﻲ ﻫﺬه اﻟﻼﺋﺤﺔ اﻟﻤﻌﺎﻧﻲ اﻟﻤﻮﺿﺤﺔ أﻣﺎم ﻛﻞ ﻣﻨﻬﺎ ﻓﻲ اﻟﻤﺎدة )اﻷوﻟﻰ( ﻣﻦ
  ﻧﻈﺎم ﺣﻤﺎﻳﺔ اﻟﺒﻴﺎﻧﺎت اﻟﺸﺨﺼﻴﺔ، اﻟﺼﺎدر ﺑﺎﻟﻤﺮﺳﻮم اﻟﻤﻠﻜﻲ رﻗﻢ )م/19( وﺗﺎرﻳﺦ9/2/1443 ﻫـ
  واﻟﻤﻌﺪل ﺑﻤﻮﺟﺐ اﻟﻤﺮﺳﻮم اﻟﻤﻠﻜﻲ رﻗﻢ )م/148( وﺗﺎرﻳﺦ5/9/1444، ﻫـ
  ```
- **نموذج عنوان مادة (المادة الأولى):**
  ```
  اﻟﻤﺎدة
  ﺗﻜﻮن ﻟﻠﻜﻠﻤﺎت واﻟﻌﺒﺎرات اﻟﻮاردة ﻓﻲ ﻫﺬه اﻟﻼﺋﺤﺔ اﻟﻤﻌﺎﻧﻲ اﻟﻤﻮﺿﺤﺔ أﻣﺎم ﻛﻞ ﻣﻨﻬﺎ ﻓﻲ اﻟﻤﺎدة )اﻷوﻟﻰ( ﻣﻦ
  ﻧﻈﺎم ﺣﻤﺎﻳﺔ اﻟﺒﻴﺎﻧﺎت اﻟﺸﺨﺼﻴﺔ، اﻟﺼﺎدر ﺑﺎﻟﻤﺮﺳﻮم اﻟﻤﻠﻜﻲ رﻗﻢ )م/19( وﺗﺎرﻳﺦ9/2/1443 ﻫـ
  ```
  **التقييم:** استخراج جيد — نص عربي مقروء بأشكال عرضية (presentation forms). مناسب لجرد المواد. بعض الأحرف تستخدم أشكالاً عرضية لكنها قابلة للمعالجة.

### ملف 4: PDPL_Implementing_Regulation_English.pdf

- **القابلية للاستخراج:** نعم — نص إنجليزي سليم
- **إجمالي الأحرف المستخرجة:** 49,855
- **نموذج النص (صفحة 1، أول 500 حرف):**
  ```
  Article 1: Definitions
  The terms and phrases used in this Regulation shall have the meanings assigned to them
  in Article (1) of the Personal Data Protection Law issued by Royal Decree No. (M/19)
  dated 9/2/1443H and amended by Royal Decree No. (M/148) dated 5/9/1444 AH. The
  following terms and phrases - wherever used in this Regulation - shall have the meanings
  assigned to them, unless the context requires otherwise:
  1. Regulation: The Implementing Regulation of the Law.
  2. Dir
  ```
- **نموذج عنوان مادة (Article 1):**
  ```
  Article 1: Definitions
  The terms and phrases used in this Regulation shall have the meanings assigned to them
  in Article (1) of the Personal Data Protection Law issued by Royal Decree No. (M/19)
  ```
  **التقييم:** استخراج ممتاز — نص سليم وقابل للقراءة.

---

## بيانات المصدر الوصفية الناقصة أو الغامضة (Missing/Ambiguous Source Metadata)

| البند | الملف | الحالة |
|-------|-------|--------|
| المرجع القانوني (المرسوم الملكي/رقم/تاريخ) | النظام العربي PDF | غير قابل للتحقق — نص مشوّه تطلب OCR |
| المرجع القانوني (المرسوم الملكي/رقم/تاريخ) | النظام الإنجليزي PDF | لم يُعثر على مرجع صريح للمرسوم الملكي في النص المستخرج (البيانات الوصفية تشير إلى «V2-23April2023-Reviewed» — ليس مرجع صدور رسمي) |
| مرجع سلطة الإصدار (SDAIA / هيئة البيانات) | اللائحة العربية PDF | وُجد مرجع «هيئة الحكومة الرقمية» في النص — لا يوجد مرجع صريح لـ SDAIA بالاسم في النص المستخرج |
| صفة الترجمة الرسمية | ملفات PDF الإنجليزية (النظام + اللائحة) | لم يُعثر على إعلان صريح عن صفة الترجمة الرسمية داخل النص أو البيانات الوصفية |
| تصنيف النظام مقابل اللائحة | النظام العربي PDF | العنوان في البيانات الوصفية يذكر «نظام حماية البيانات الشخصية ولوايحه التنظيمية ١» — يشير إلى أنه الجزء ١ (النظام). النص غير قابل للتحقق مباشرة. |
| تصنيف النظام مقابل اللائحة | اللائحة العربية PDF | العنوان في البيانات الوصفية يذكر «نظام حماية البيانات الشخصية ولوايحه التنظيمية ٢» — يشير إلى أنه الجزء ٢ (اللائحة). النص العربي المستخرج يؤكد: «اللائحة التنفيذية للنظام». |

---

## قيمة الجاهزية الإجمالية (Overall Readiness Value)

### `NEEDS_OCR_BEFORE_PDPL_INVENTORY`

**السبب:**
- جميع ملفات PDF الأربعة المتوقعة موجودة ✓
- ملف PDF العربي للائحة التنفيذية موجود وقابل للاستخراج النصي ✓
- ملفات PDF الإنجليزية موجودة وقابلة للاستخراج ✓
- **لكن:** ملف PDF العربي للنظام الأساسي (المصدر الحاكم للنظام) **غير قابل للاستخراج النصي** — الخطوط المدمجة تستخدم ترميز Identity-H بدون ToUnicode CMap صالح، مما ينتج نصاً مشوّهاً تماماً غير قابل للاستخدام في جرد المواد. مطلوب OCR قبل جرد المواد.

---

## المرحلة التالية الموصى بها (Recommended Next Stage)

### `PDPL_SOURCE_PACKET_OCR_PREP`

**السبب:** ملف PDF العربي للنظام الأساسي يحتاج OCR قبل أن يكون جاهزاً لجرد المواد على مستوى المقالات. اللائحة العربية لا تحتاج OCR (نصها قابل للاستخراج). ملفات الإنجليزية مرجعية ولا تؤثر على الجاهزية.

---

## نتائج التحقق (Validation Results)

### `make validate`

```
============================================================
Saudi Companies Law — Book 1 corpus validation
============================================================
[PASS] schema
------------------------------------------------------------
RESULT: ALL CHECKS PASSED ✓
```

**النتيجة:** نجاح ✓ (لا علاقة بـ PDPL — التحقق الحالي مخصص لنظام الشركات Book 1)

### `make test`

```
14 failed, 2483 passed in 29.29s
```

**النتيجة:** 14 فشل — جميعها **أعطال أساسية معروفة (known baseline failures)** متعلقة بـ Chinese translation remediation batch tests (P1-003، P2-002، P2-003). لا علاقة لها بـ PDPL. لم يتم إدخال أي فشل جديد.

**الفشلات المعروفة (Baseline failures):**
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

**لم يتم إصلاح أي فشل غير متعلق بهذه المرحلة.** لا فشلات جديدة.

---

## قسم التأكيدات (Confirmations)

- ✅ **لم يتم تنفيذ (commit) ملف ZIP** — تم فحصه محلياً فقط في `tmp_pdpl_source_packet_audit/` (untracked)
- ✅ **لم يتم تنفيذ (commit) أي ملف PDF** — تم استخراجها في مجلد مؤقت untracked فقط
- ✅ **لم يتم تنفيذ (commit) أي نص مستخرج** — تم فحص العينات في الذاكرة فقط ولم تُكتب كملفات
- ✅ **لم يحدث أي استيعاب (ingestion)** — لا سجلات، لا مخططات، لا مدققات
- ✅ **لم يتم إنشاء سجلات JSONL**
- ✅ **لم يتم إنشاء مخططات (schemas)**
- ✅ **لم يتم إنشاء مدققات (validators)**
- ✅ **لم يتم تعديل ملفات قانون العمل (Labor Law)**
- ✅ **لم يتم تعديل ملفات نظام الشركات (Companies Law)**
- ✅ **لا تعديلات runtime / API / RAG / UI / embeddings**
- ✅ **الحدود العربية الحاكمة مؤكدة** — النظام العربي واللائحة العربية هما المصدران الحاكمان، الإنجليزية مرجعية فقط
- ✅ **الحدود الإنجليزية المرجعية مؤكدة** — ملفات PDF الإنجليزية مرجعية فقط ولا تحكم على العربية
- ✅ **لا نصيحة قانونية / لا تفسير قانوني** — هذا تقرير جرد فني فقط

---

## الملف الوحيد المنشأ (Only File Created)

```
reports/pdpl/PDPL_SOURCE_PACKET_INVENTORY_AND_BOUNDARY_AUDIT_REPORT.md
```

---

*تم إعداد هذا التقرير كمرحلة تأسيسية لإضافة نظام حماية البيانات الشخصية (PDPL) كمسار قانوني تالي بعد قانون العمل ونظام الشركات.*