# تقرير تصحيح دلالات عرض مواد نظام العمل في BOE بعد PR #147

## المرحلة (Stage)

LABOR_LAW_BOE_ARTICLE_DISPLAY_SEMANTICS_CORRECTION_AFTER_PR_147

## رقم الالتزام الأساسي (Baseline SHA)

ac1980ebc1acc0a95698e5891cccb613031338ee

## النطاق (Scope)

مرحلة تدقيق وتصحيح فقط (report-only correction audit). لا استدراك. لا تعديل CSV. لا إنشاء دفعة. لا إدخال نهائي.

## نموذج عرض BOE المصحح (Corrected BOE display model)

### الافتراض السابق (في PR #147) — غير صحيح

كان PR #147 يفترض أن نافذة التعديل (popup) في BOE يجب أن تعرض النص الكامل الحالي للمادة بعد التعديل بصيغة "لتكون بالنص الآتي"، وأن غياب النص الكامل في النافذة يعني أن المادة محظورة. **هذا الافتراض كان غير صحيح.**

### النموذج المصحح

نافذة التعديل (popup) في BOE هي **بيانات تاريخية للتعديل فقط** (amendment history metadata) — وليست مصدراً للنص الكامل الحالي. النافذة تصف نوع التعديل (استبدال كلمة، إضافة عبارة، تعديل فقرة) كبيانات وصفية. هذا السلوك متوقع وطبيعي من BOE.

المصدر المتوقع للنص الحالي هو **المتن الرئيسي للمادة** (main article body) في BOE. المتن الرئيسي قد يكون:
1. النص الحالي المحين بعد التعديل (إذا قام BOE بتحديث المتن)
2. النص الأصلي قبل التعديل (إذا لم يقم BOE بتحديث المتن بعد)

### منهجية التحقق

لكل مادة من المواد الـ8:
1. قراءة المتن الرئيسي من BOE
2. قراءة نافذة التعديل (metadata فقط)
3. فحص ما إذا كان المتن الرئيسي يعكس التعديل المذكور في النافذة

التحقق العملي:
- إذا قالت النافذة "استبدل كلمة X بكلمة Y": فحص ما إذا كان المتن الرئيسي يستخدم Y
- إذا قالت النافذة "أضف عبارة Z": فحص ما إذا كان المتن الرئيسي يتضمن Z
- إذا قالت النافذة "عدل الفقرة 1 لتكون بالنص الآتي": فحص ما إذا كانت الفقرة 1 في المتن الرئيسي تطابق النص المعدل

## المصدر (Source)

- URL: https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- الجهة المصدرية: مكتب الخبراء بمجلس الوزراء — النظام الرسمي للوثائق النظامية
- تاريخ الوصول: 2026-07-08

## المواد الـ8 المراجعة (Exact 8 articles reviewed)

1. labor_law_art_022
2. labor_law_art_023
3. labor_law_art_024
4. labor_law_art_025
5. labor_law_art_027
6. labor_law_art_028
7. labor_law_art_031
8. labor_law_art_040

## جدول التدقيق المصحح article-by-article

| article_key | article_number | boe_main_body_status | popup_role | amendment_visible | evidence_summary | corrected_classification | recommended_next_action |
|---|---|---|---|---|---|---|---|
| labor_law_art_022 | 22 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: تعديل صدر المادة + تعديل الفقرة 3/3 | المتن الرئيسي يستخدم "وحدات" (قديم) وليس "قنوات" (جديد)؛ الفقرة 3/3 تستخدم "إحالة طلبات العمال" (قديم) وليس "مواءمة طلبات طالبي العمل" (جديد). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_023 | 23 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: إحلال "قنوات" محل "وحدة"/"وحدات" | المتن الرئيسي يستخدم "وحدة التوظيف" (قديم) وليس "قنوات التوظيف" (جديد). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_024 | 24 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: إحلال "قنوات" محل "وحدة"/"وحدات" | المتن الرئيسي يستخدم "وحدات التوظيف" (قديم) وليس "قنوات التوظيف" (جديد). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_025 | 25 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: إحلال "قنوات" + إحلال "الوزارة" محل "مكتب العمل المختص" | المتن الرئيسي يستخدم "وحدة التوظيف" (قديم) وليس "قنوات" (جديد)؛ ويستخدم "مكتب العمل المختص" (قديم) وليس "الوزارة" (جديد). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_027 | 27 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: إحلال "قنوات" محل "وحدة"/"وحدات" | المتن الرئيسي يستخدم "وحدات التوظيف" (قديم) وليس "قنوات التوظيف" (جديد). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_028 | 28 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: 3 استبدالات (قنوات + الوزارة + ذوو الإعاقة) | المتن الرئيسي يستخدم "وحدات" (قديم) وليس "قنوات"؛ "مكتب العمل المختص" (قديم) وليس "الوزارة"؛ "المعوقون" (قديم) وليس "ذوو الإعاقة". المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_031 | 31 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: إضافة عبارة "أو الشركات" بعد "المكاتب" | المتن الرئيسي يتضمن "المكاتب" ولكن لا يتضمن "أو الشركات" (الإضافة الجديدة غير موجودة). المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |
| labor_law_art_040 | 40 | OLD_BASE_TEXT_NOT_UPDATED | amendment_history_metadata | نافذة م/44: تعديل الفقرة 1 بالنص الآتي | المتن الرئيسي للفقرة 1 لا يتضمن عبارة "يتسبب بها صاحب العمل" (النص المعدل الجديد). الفقرة 1 تستخدم الصياغة القديمة. المتن لم يُحدَّث. | STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | إيقاف المادة حتى توفير مصدر رسمي يحتوي على النص المحين |

## العدد حسب التصنيف المصحح (Exact count per corrected_classification)

| corrected_classification | count |
|---|---|
| REMEDIABLE_FROM_BOE_MAIN_BODY_CURRENT_TEXT | 0 |
| STILL_BLOCKED_MAIN_BODY_NOT_UPDATED | 8 |
| NEEDS_OPERATOR_REVIEW | 0 |
| **الإجمالي** | **8** |

تفصيل العدد:
- REMEDIABLE_FROM_BOE_MAIN_BODY_CURRENT_TEXT: 0 — لا توجد أي مادة من المواد الـ8 يحتوي متنها الرئيسي على النص المحين بعد التعديل
- STILL_BLOCKED_MAIN_BODY_NOT_UPDATED: 8 — جميع المواد الـ8 يعرض BOE فيها النص الأصلي/الأساسي قبل التعديل (م/44)، والمتن لم يُحدَّث ليعكس التعديل
- NEEDS_OPERATOR_REVIEW: 0

## هل يحتاج تصنيف PR #147 إلى تصحيح؟ (Whether PR #147 classification needs correction)

**نعم — السبب المنطقي للتصنيف يحتاج إلى تصحيح، لكن النتيجة النهائية تبقى كما هي.**

### ما كان خطأ في PR #147

الافتراض أن "غياب النص الكامل في نافذة التعديل يعني أن المادة محظورة" كان غير صحيح. نافذة التعديل في BOE هي بيانات تاريخية وصفية للتعديل فقط، وليست متوقعة أن تعرض النص الكامل الحالي. هذا سلوك متوقع من BOE وليس عيباً في المصدر.

### ما تبقى صحيحاً من نتيجة PR #147

نتيجة "محظور" (BLOCKED) للمواد الـ8 لا تزال صحيحة، لكن **لسبب مختلف**: المتن الرئيسي في BOE لهذه المواد يعرض النص الأصلي/الأساسي (قبل تعديل م/44) ولم يُحدَّث ليعكس التعديل. هذا يعني أن BOE نفسه لم يقم بتحديث متون هذه المواد بعد تطبيق مرسوم م/44 (بتاريخ 1446/2/8هـ، يعمل به من 1446/8/20هـ).

### الفرق العملي

- PR #147 قال: "محظور لأن النافذة لا تعرض النص الكامل" — **سبب غير صحيح**
- هذا التقرير يقول: "محظور لأن المتن الرئيسي في BOE لم يُحدَّث بعد التعديل" — **سبب صحيح ومتحقق منه بالدليل**

النتيجة النهائية (BLOCKED) صحيحة، لكن السبب والمنهجية تم تصحيحها.

## هل دفعة استدراك آمنة الآن؟ (Whether a remediation batch is now safe)

**لا** — لا توجد دفعة استدراك آمنة لهذه المواد الـ8 في هذه المرحطة. جميع المواد الـ8 يعرض BOE فيها النص الأصلي قبل التعديل. المتن الرئيسي لم يُحدَّث. لا يمكن استخدام المتن الرئيسي كنص حالي لأنه لا يعكس تعديل م/44. ولا يمكن استخدام نافذة التعديل لتركيب النص لأن النافذة تعطي تعليمات تعديل جزئية فقط.

## المرحلة التالية الموصى بها (Recommended next stage)

PARK_BLOCKED_ARTICLES_MAIN_BODY_NOT_UPDATED

السبب: جميع المواد الـ8 يعرض BOE فيها النص الأصلي قبل تعديل م/44. المتن الرئيسي لم يُحدَّث. لا يوجد مصدر رسمي بديل متاح حالياً يحتوي على النص الكامل المحين لهذه المواد. يجب إيقاف هذه المواد حتى:
1. يقوم BOE بتحديث متون هذه المواد ليعكس تعديل م/44، أو
2. يوفر المشغّل مصدراً رسمياً بديلاً يحتوي على النص الكامل المحين

## تأكيدات الحدود (Boundary confirmations)

- لا تعديل CSV: مؤكد
- لا تغيير في ملفات English: مؤكد
- لا استدراك عربي: مؤكد
- لا إدخال نهائي: مؤكد
- المصدر العربي الرسمي يحكم: مؤكد
- لا استشارة قانونية / لا تفسير قانوني: مؤكد
- لا تركيب نص أساسي + نافذة: مؤكد
- لا توليد نص قانوني: مؤكد

## نتائج التحقق (Validation results)

- `make validate`: PASS — جميع الفحوصات اجتازت بنجاح ✓
- `make test`: 14 failures, 2483 passed
  - جميع 14 فشل هي فشل معروف مسبق (known baseline failures) في اختبارات الصينية (test_chinese_*) — غير متعلقة بنظام العمل أو هذه المرحلة
  - فشل جديد تم إدخاله: لا يوجد
  - لم يتم إصلاح أي فشل غير متعلق بهذه المرحلة

تفصيل الفشل المعروف مسبق (all Chinese-related, pre-existing on main):
1. test_chinese_all_babs_source_inventory.py::test_generator_is_byte_stable
2. test_chinese_internal_legal_llm_isolable_source_articles.py::test_chinese_text_exact_and_hash
3. test_chinese_internal_legal_llm_isolable_source_articles.py::test_generator_is_byte_stable
4. test_chinese_internal_llm_semantic_qa_gap_plan.py::test_generator_is_byte_stable
5. test_chinese_remediation_backlog_source_packet_plan.py::test_generator_is_byte_stable
6. test_chinese_remediation_batch_p1_003.py::test_validator_passes_on_current_outputs
7. test_chinese_remediation_batch_p1_003.py::test_prior_candidate_link_matches_unchanged_candidate
8. test_chinese_remediation_batch_p1_003_qa.py::test_validator_passes_on_current_outputs
9. test_chinese_remediation_batch_p2_002.py::test_validator_passes_on_current_outputs
10. test_chinese_remediation_batch_p2_002.py::test_prior_candidate_link_matches_unchanged_candidate
11. test_chinese_remediation_batch_p2_002_qa.py::test_validator_passes_on_current_outputs
12. test_chinese_remediation_batch_p2_003.py::test_validator_passes_on_current_outputs
13. test_chinese_remediation_batch_p2_003.py::test_prior_candidate_link_matches_unchanged_candidate
14. test_chinese_remediation_batch_p2_003_qa.py::test_validator_passes_on_current_outputs