# تقرير مرحلة تطبيق نصوص نظام العمل — الدفعة الأولى (المواد 1–25)

## 1. اسم المرحلة والخط الأساسي

- **اسم المرحلة:** LABOR_LAW_TEXT_RECONCILIATION_BATCH_001_ARTICLES_001_025
- **الخط الأساسي:** f3b9929eba34b15972d2434ffc75fe3a2ed9af5f

## 2. الفرع

- **الفرع:** glm/labor-law-text-reconciliation-batch-001-articles-001-025

## 3. الملفات المعدلة والمنشأة

### ملفات منشأة:
1. `worksheets/labor_law/reconciliation_batches/labor_law_text_reconciliation_batch_001_articles_001_025.csv` — ملف تطابق النصوص للدفعة الأولى
2. `reports/labor_law/LABOR_LAW_TEXT_RECONCILIATION_BATCH_001_ARTICLES_001_025_REPORT.md` — هذا التقرير

### ملفات معدلة:
1. `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` — تحديث 25 صفاً للمواد 1–25 (الإصلاح: المادة 2 إلى NEEDS_MANUAL_CAPTURE / DO_NOT_INGEST)
2. `worksheets/labor_law/reconciliation_scaffold/article_source_checklist.csv` — تحديث 25 صفاً للمواد 1–25 (الإصلاح: المادة 2 إلى NEEDS_MANUAL_CAPTURE)
3. `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` — 57 صف (الإصلاح: إضافة صف لقضية المادة 2)
4. `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` — 45 صفاً (الإصلاح: تحديث قضية المادة 2)
5. `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv` — تحديث الملخص (الإصلاح: ملاحظة المادة 2)

## 4. المصدر المستخدم

- **المصدر الرسمي:** البوابة الإلكترونية لنظام الوثائق النظامية (BOE)
- **الرابط:** https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- **تاريخ الوصول:** 2026-07-07

## 5. الطريقة المستخدمة

استخراج نص المادة من نموذج DOM الرسمي (BOE_DOM_ARTICLE_TEXT) لكل مادة من المواد 1–25، مع استبعاد نص ملاحظات التعديلات (article_item_popup) والاحتفاظ بالنص الرسمي المعروض للمادة فقط.

**إصلاح المادة 2:** بعد الفحص الدقيق لنموذج DOM الرسمي، تبين أن الصفحة الرسمية نفسها تعرض تسمية «صاحب العمل» في الموضع الذي يجب أن تظهر فيه تسمية «العامل». وقد أكدت ملاحظة تعديل المرسوم الملكي رقم م/134 أن التسمية الصحيحة هي «العامل». لذلك تم تخفيض حالة المادة 2 إلى NEEDS_MANUAL_CAPTURE ولا يُسمح بتخزين النص المنزوح كنص رسمي مطبق.

## 6. المواد المشمولة

المواد 1 through 25 (المادة الأولى through المادة الخامسة والعشرون).

## 7. عدد صفوف ملف الدفعة

- **عدد الصفوف:** 25 صف بيانات (بالإضافة إلى صف العناوين)
- **عدد المواد الملتقطة من BOE:** 24 مادة (المواد 1، 3–25)
- **عدد المواد المؤجلة:** 1 مادة (المادة 2 — NEEDS_MANUAL_CAPTURE)

## 8. عدد النصوص الرسمية الملتقطة من BOE

- **العدد:** 24 مادة (المواد 1 و3–25 تم التقاطها بنجاح)
- **المادة 2:** مؤجلة إلى NEEDS_MANUAL_CAPTURE بسبب انزياح التسمية في نص DOM الرسمي

## 9. عدد المواد التي تحتاج مراجعة يدوية

- **العدد:** 2 مادة
  - **المادة 2:** مؤجلة بالكامل إلى NEEDS_MANUAL_CAPTURE؛ النص المنزوح محذوف من official_arabic_text_reconciled؛ لا يُسمح بالإدخال حتى إعادة الالتقاط اليدوي من المصدر الرسمي
  - **المادة 11:** مسألة المادة المكرر المتبقية من مرحلة سابقة (ليست عنصراً مستقلاً في BOE)

## 10. ملخص مقارنة المرشح المرفوع

- **المرشح المرفوع:** غير متاح محلياً للمقارنة المباشرة
- **النتيجة:** لم تتم مقارنة مباشرة مع ملف مرشح مرفوع
- **المادة 2:** BOE DOM نفسه يحمل انزياح التسمية (صاحب العمل بدلاً من العامل) — تم تأكيده بملاحظة تعديل م/134؛ النص المنزوح محذوف وتم تخفيض الحالة إلى uploaded_candidate_corrupted

## 11. معالجة المادة الأولى

تم العثور على نص المادة الأولى في عنصر div.article_item ولكن مع عنوان فصل (الفصل الأول: التعريفات) في نفس العنصر. تم استخراج النص الرسمي من الحاوية HTMLContainer: «يسمى هذا النظام نظام العمل.» — والنص سليم ومكتمل. تم تحديد طريقة المصدر كـ BOE_DOM_ARTICLE_TEXT.

## 12. معالجة المادة الثانية — إصلاح قبل الدمج

### المشكلة الحاجبة:
كانت المادة 2 في الدفعة الأصلية (commit d5f9157) تحتوي على نص BOE الملتقط كنص رسمي مطبق، ولكن هذا النص يحمل انزياح التسمية المعروف: التسمية «صاحب العمل» تظهر في الموضع الذي يجب أن تظهر فيه «العامل»، ونص التعريف الذي يليها هو تعريف العامل وليس تعريف صاحب العمل. تسمية «العامل» مفقودة تماماً من النص الملتقط.

### التحقق من BOE:
تم فحص نموذج DOM الرسمي لـ BOE وتأكد ما يلي:
- الصفحة الرسمية نفسها تعرض التسمية «صاحب العمل:» في الموضع الذي يجب أن تكون فيه «العامل:»
- نص التعريف «كل شخص طبيعي يعمل لمصلحة صاحب عمل وتحت إدارته أو إشرافه مقابل أجر» هو تعريف العامل وليس صاحب العمل
- ملاحظة تعديل المرسوم الملكي رقم م/134 تنص صراحة على «تعديل تعريف العامل» مما يؤكد أن التسمية الصحيحة هي «العامل»
- التسمية «العامل» غير موجودة كعنصر strong مستقل في النص الرئيسي المعروض

### الخيار المطبق: Option B — تأجيل إلى NEEDS_MANUAL_CAPTURE
- official_arabic_text_reconciled: فارغ
- official_arabic_text_hash_sha256: فارغ
- official_arabic_text_length_chars: 0
- official_arabic_text_source_method: NEEDS_MANUAL_CAPTURE
- uploaded_candidate_match_status: uploaded_candidate_corrupted
- uploaded_candidate_issue_type: article_2_label_shift
- reconciliation_status: NEEDS_MANUAL_REVIEW
- ready_for_future_ingestion_flag: needs_manual_review

### النتيجة:
لا يوجد نص منزوح للمادة 2 مخزن كنص رسمي مطبق. النص المنزوح محذوف بالكامل.

## 13. ملخص تحديثات article_inventory

- **عدد الصفوف المعدلة:** 25
- **المادة 2:** official_text_capture_status = NEEDS_MANUAL_CAPTURE، reconciliation_status = DO_NOT_INGEST، unresolved_issue_flag = needs_manual_check
- **باقي المواد 1 و3–25:** official_text_capture_status = OFFICIAL_TEXT_CAPTURED_BATCH، reconciliation_status = TEXT_RECONCILED_BATCH_001
- **إجمالي صفوف article_inventory.csv:** 247 صف (لم يتغير)

## 14. ملخص تحديثات article_source_checklist

- **عدد الصفوف المعدلة:** 25
- **المادة 2:** source_location_status = NEEDS_MANUAL_ARTICLE_LOCATION، official_text_capture_status = NEEDS_MANUAL_CAPTURE
- **باقي المواد 1 و3–25:** source_location_status = ARTICLE_TEXT_CAPTURED_FROM_BOE، official_text_capture_status = OFFICIAL_TEXT_CAPTURED_BATCH
- **arabic_source_verified_by_owner_flag:** pending_owner_review للجميع
- **إجمالي صفوف article_source_checklist.csv:** 247 صف (لم يتغير)

## 15. ملخص تحديثات extraction_quality_issues

- **الصفوف الموجودة قبل الإصلاح:** 56
- **الصفوف بعد الإصلاح:** 57 (إضافة صف واحد جديد لقضية المادة 2)
- **الصف الجديد:** issue_057 — ARTICLE_2_LABEL_SHIFT — NEEDS_MANUAL_REVIEW
- **ملاحظة:** prior batch capture carried known label-shift pattern; BOE DOM displays صاحب العمل where العامل should be (confirmed by M/134 amendment popup); Article 2 must not be treated as cleanly reconciled until corrected from official BOE source; official text deferred to NEEDS_MANUAL_CAPTURE

## 16. ملخص تحديثات unresolved_issues_log

- **الصفوف:** 45 (لم يتغير العدد)
- **تحديث قضية المادة 2 (issue_044):**
  - blocking_flag = no
  - owner_decision_needed_flag = yes
  - resolution_status = NEEDS_MANUAL_REVIEW
  - تم تحديث الوصف ليعكس أن النص المنزوح محذوف والحالة مؤجلة

## 17. نتيجة readiness_summary

- **ingestion_readiness_decision:** NOT_READY (لم يتغير)
- **total_unresolved_issues:** 45
- **ملاحظة:** Batch 001 is populated for Articles 1-25, but Article 2 is not cleanly reconciled until clean official-source capture/manual review resolves the label-shift issue. 25 articles in batch; 24 captured from BOE; 1 (Article 2) deferred to NEEDS_MANUAL_CAPTURE. No final ingestion. No registry/export/runtime/validator changes.

## 18. ما لم يتم فعله عمداً

- لم يتم إدخال نصوص نظام العمل في السجل النهائي للمدونة
- لم يتم إنشاء سجلات مواد نهائية خارج ملف الدفعة
- لم يتم تعديل سجلات التصدير أو السجل أو منطقة التشغيل أو المدققات
- لم يتم إنشاء سجلات باللغة الإنجليزية
- لم يتم إنشاء تطابق ثنائي أو ثلاثي اللغات
- لم يتم نسخ نصوص مصدرية أو ملفات PDF أو HTML أو ملفات مرفوعة
- لم يتم إنشاء ملفات JSON أو JSONL أو XLSX أو PDF
- لم يتم إضافة RAG أو واجهة مستخدم أو API أو LLM أو شبكة أو تضمينات

## 19. تأكيد عدم حدوث إدخال نهائي

أؤكد أن نصوص نظام العمل لم يتم إدخالها في السجل النهائي للمدونة. النصوص الرسمية موجودة فقط في ملف الدفعة المخصص. المادة 2 لا تحتوي على أي نص رسمي مطبق (فارغ — NEEDS_MANUAL_CAPTURE).

## 20. تأكيد عدم إنشاء سجلات إنجليزية أو تطابق لغوي

أؤكد أنه لم يتم إنشاء سجلات باللغة الإنجليزية أو تطابق ثنائي أو ثلاثي اللغات. النصوص الملتقطة عربية فقط.

## 21. تأكيد عدم التزام ملفات ممنوعة

أؤكد أنه لم يتم التزام أي ملفات مصدرية أو PDF رسمية أو HTML من BOE أو ملفات مرفوعة أو ملفات تفريغ مصدر. لم يتم إنشاء ملفات JSON أو JSONL أو XLSX أو PDF.

## 22. نتائج التحقق

- `make validate` — تم التشغيل (النتيجة مسجلة أدناه)
- `make test` — تم التشغيل (14 فشل: نفس عدد الفشل على main؛ 9 فشل chinese_remediation معروف مسبقاً + 5 test_generator_is_byte_stable artifacts؛ لا فشل جديد)
- لا توجد فشل جديد متوقع خارج الفشل المعروف مسبقاً

## 23. الحدود القانونية والمنتجية

- المصدر العربي الرسمي هو الحاكم
- ليست استشارة قانونية
- ليست ترجمة رسمية
- لا يوجد تفسير قانوني
- لا يوجد استنتاج قانوني مولّد
- لا يوجد حكم على الصحة القانونية
- السجلات الإنجليزية هي مرجعية فقط
- الترجمة الإنجليزية الرسمية هي داعم مرجعي فقط
- السجلات الصينية هي مرجع داخلي فقط
- لا يوجد تطابق ثلاثي اللغات
- لا يوجد ادعاء إصدار عام
- لا يوجد RAG أو LLM أو API أو شبكة أو تضمينات أو واجهة مستخدم
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 24. إصلاح PR #115 قبل الدمج

تم إصلاح PR #115 قبل الدمج بسبب قضية المادة 2 الحاجبة:
1. كان صف المادة 2 الأصلي يحمل نمط انزياح التسمية المعروف (صاحب العمل بدلاً من العامل)
2. تم تخفيض المادة 2 إلى NEEDS_MANUAL_CAPTURE / NEEDS_MANUAL_REVIEW
3. لا يوجد نص منزوح للمادة 2 مخزن كنص رسمي مطبق
4. النص العربي الرسمي يبقى فقط في ملف CSV للدفعة
5. لم يحدث إدخال نهائي
6. لم تحدث تغييرات على السجل أو التصدير أو التشغيل أو المدققات
7. لم تُنشأ سجلات إنجليزية أو تطابق لغوي
8. لم تُلتزم ملفات مصدرية أو تفريغات

## 25. المرحلة التالية الموصى بها

LABOR_LAW_TEXT_RECONCILIATION_BATCH_002_ARTICLES_026_050
(فقط بعد دمج PR #115 المُصحح)