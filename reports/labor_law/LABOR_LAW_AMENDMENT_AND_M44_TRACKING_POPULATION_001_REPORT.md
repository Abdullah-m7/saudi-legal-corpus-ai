# تقرير تعبئة تتبع التعديلات والمرسوم م/44 لنظام العمل — تعبئة بنيوية فقط

**المرحلة:** LABOR_LAW_AMENDMENT_AND_M44_TRACKING_POPULATION_001
**الأساس المعتمد (main HEAD):** cbd42026b26b2b01531ced170ee1b50a04882c07
**الفرع:** glm/labor-law-amendment-m44-tracking-population-001
**التاريخ:** 2026-07-07

---

## 1. اسم المرحلة والأساس

- **المرحلة:** LABOR_LAW_AMENDMENT_AND_M44_TRACKING_POPULATION_001
- **الأساس المعتمد (main HEAD):** cbd42026b26b2b01531ced170ee1b50a04882c07
- **الفرع:** glm/labor-law-amendment-m44-tracking-population-001

---

## 2. الملفات المُعدّلة

- worksheets/labor_law/reconciliation_scaffold/amendment_tracking.csv (تعبئة بنيوية)
- worksheets/labor_law/reconciliation_scaffold/m44_tracking.csv (تعبئة بنيوية)
- worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv (تعبئة بنيوية)
- worksheets/labor_law/reconciliation_scaffold/article_inventory.csv (تحديث أعلام بنيوية)
- worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv (تحديث الملخص)

## 3. الملفات المُنشأة

- reports/labor_law/LABOR_LAW_AMENDMENT_AND_M44_TRACKING_POPULATION_001_REPORT.md (هذا التقرير)

---

## 4. المصدر المُستخدم

- **المصدر الرسمي الحاكم:** بوابة القوانين والتنظيمات السعودية (laws.boe.gov.sa)
- **الرابط:** https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- **تاريخ الوصول:** 2026-07-07
- **طبيعة الاستخدام:** استخراج بنيوي فقط (أرقام المراسيم، تواريخ التعديلات، علامات م/44، علامات الإلغاء/الحذف/الإضافة)
- **لم يُنسخ أي نص قانوني من المصدر الرسمي**
- **المراجع السابقة المُستخدمة كمساعدة هيكلية:**
  - reports/labor_law/LABOR_LAW_ARTICLE_INVENTORY_POPULATION_001_REPORT.md
  - reports/labor_law/LABOR_LAW_UPLOADED_SOURCE_AUDIT_REPORT.md
  - reports/labor_law/LABOR_LAW_OFFICIAL_UNIFIED_SOURCE_INVENTORY_REPORT.md
  - reports/labor_law/LABOR_LAW_RECONCILIATION_WORKSHEET_DESIGN.md

---

## 5. الطريقة المُستخدمة

1. تم الوصول إلى صفحة نظام العمل الرسمية على laws.boe.gov.sa
2. تم استخراج جميع عناصر `article_item.changed-article` من DOM الصفحة (106 مادة)
3. تم استخراج جميع نوافذ ملاحظات التعديل `article_item_popup` (127 نافذة)
4. تم استخراج أرقام المراسيم وتواريخها من نصوص النوافذ:
   - المرسوم م/44: 45 نافذة تعديل
   - المرسوم م/46: نافذة واحدة
   - المرسوم م/5: 4 نوافذ
   - المرسوم م/134: 4 نوافذ
   - مراسيم أخرى: بقية النوافذ
5. تم تحديد نطاق التعديل لكل نافذة (تعديل، إلغاء، حذف، إضافة، مكرر، إعادة ترقيم)
6. تم تعبئة ملفات CSV الخمسة بالبيانات البنيوية فقط

---

## 6. عدد صفوف amendment_tracking المُعبّأة

- **عدد صفوف البيانات:** 127
- **عدد المواد الممثلة:** 106 (مادة معدلة + إدخالات معاد ترقيمها)
- **توزيع المراسيم:**
  - م/44: 45 نافذة تعديل
  - م/46: نافذة واحدة (المادة 74)
  - م/5: 4 نوافذ (المواد 131، 149، 150، 186)
  - م/134: 4 نوافذ (المواد 2، 3، 155، 156)
  - بدون رقم مرسوم محدد: 73 نافذة (مرسوم م/46 بتاريخ 5/6/1436 في الغالب)

---

## 7. عدد صفوف m44_tracking المُعبّأة

- **عدد صفوف البيانات:** 45
- **عدد المواد المتأثرة بـ م/44:** 45 مادة فريدة
- **المادة الثانية:** ممثلة مع `article_2_definition_added_flag = yes` و `added_terms = الإسناد؛ الاستقالة`
- **نطاق المواد المتأثرة:** المواد 2، 7، 22-28، 30-31، 35، 37، 39-40، 42-48، 51-53، 61، 72، 74-75، 107، 113، 151، 168، 178، 182، 195-199، 203، 205-209، 230

---

## 8. عدد صفوف unresolved_issues_log المُعبّأة

- **عدد صفوف البيانات:** 7
- **القضايا:**
  1. MUKARRAR_ARTICLE_LOCATION: المواد 11 مكرر و 131 مكرر غير موجودة كعناصر مستقلة
  2. AMENDMENT_COUNT_VARIANCE: 106 من BOE مقابل 104 من التدقيق السابق
  3. M44_MAPPING_GAP: 45 مادة من BOE مقابل 47 مرجعًا من التدقيق السابق
  4. RENUMBERED_ARTICLE_HANDLING: المادة 231/240 معاد ترقيمها
  5. RENUMBERED_ARTICLE_HANDLING: المادة 232/242 معاد ترقيمها
  6. AMENDMENT_REFERENCE_EXTRACTION: بعض النوافذ بدون رقم مرسوم مستخرج
  7. SOURCE_STRUCTURE_ANOMALY: المواد 233/234/235 مكررة على BOE (من المرحلة السابقة)

---

## 9. تحديثات article_inventory

- **amendment_count:** تم تحديثها لـ 106 مادة (بناءً على عدد نوافذ التعديل لكل مادة)
- **m44_related_flag:** تم تحديثها:
  - `yes` لـ 45 مادة مؤكدة من BOE
  - `no` لبقية المواد
- **unresolved_issue_flag:** تم تحديثها لـ `needs_manual_check` للمادتين 231_renumbered و 232_renumbered
- **reviewer_notes:** تمت إضافة ملاحظات بنيوية للمواد المعاد ترقيمها

---

## 10. نتيجة readiness_summary

- **total_articles:** 247
- **total_amended_articles:** 106
- **total_m44_related_articles:** 45 (من استخراج BOE؛ التدقيق السابق أبلغ عن 47)
- **total_mukarrar_articles:** 2
- **total_renumbered_articles:** 2
- **total_unresolved_issues:** 7
- **ingestion_readiness_decision:** NOT_READY
- **summary_notes:** structure-level amendment/M44 tracking only; no legal text captured; no reconciliation; no ingestion

---

## 11. القضايا غير المحلولة المحفوظة للمرحلة التالية

1. **المواد 11 مكرر و 131 مكرر:** لم تُوجدا على BOE كعناصر مستقلة
2. **العدد 106 مقابل 104:** اختلاف طفيف بين BOE والتدقيق السابق
3. **المرسوم م/44 (45 مقابل 47):** استخراج BOE وجد 45 نافذة تعديل لم/44 عبر 45 مادة فريدة؛ التدقيق السابق أبلغ عن 47 مرجعًا
4. **المادتان 231 و 232 المعاد ترقيمها:** تحتاجان معالجة تسوية لاحقًا
5. **بعض النوافذ بدون رقم مرسوم:** تحتاج مراجعة يدوية للنص

---

## 12. ما لم يتم تعبئته عمدًا

- **لم تُعبأ نصوص التعديلات القانونية** — لا نص عربي ولا نص إنجليزي
- **لم يتم دمج أي تعديل** (merge_decision_status = NOT_STARTED لجميع الصفوف)
- **لم يتم تحديد المعنى القانوني لأي تعديل**
- **لم تُعبأ مراجع السطور من الملف المرفوع**
- **لم يتم تحديد total_deleted_or_abolished_articles** — غير مُؤكد بشكل كامل

---

## 13. تأكيد عدم نسخ نص قانوني

- ✅ لم يُنسخ أي نص قانوني عربي من المصدر الرسمي
- ✅ لم يُنسخ أي نص قانوني إنجليزي من ملف PDF
- ✅ جميع الحقول تحتوي بيانات بنيوية فقط (أرقام مراسيم، تواريخ، علامات)

---

## 14. تأكيد عدم إجراء تسوية

- ✅ لم تتم أي تسوية نص لأي مادة
- ✅ merge_decision_status = NOT_STARTED لجميع صفوف amendment_tracking
- ✅ لم يتم دمج أي تعديل في أي نص مادة

---

## 15. تأكيد عدم إضافة نظام العمل

- ✅ لم تتم أي إضافة (ingestion) لنظام العمل
- ✅ ingestion_readiness_decision = NOT_READY
- ✅ لم تُنشأ أي سجلات مواد

---

## 16. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة

- ✅ لم تُنشأ أي سجلات إنجليزية
- ✅ لم تُنشأ أي محاذاة ثنائية أو ثلاثية اللغات
- ✅ الترجمة الإنجليزية الرسمية تبقى مرجعًا مساعدًا فقط

---

## 17. تأكيد عدم التزام ملفات مصدر

- ✅ لم يُلتزم nizam_alamal.txt أو nizam_alamal_english.pdf
- ✅ لم يُلتزم أي HTML أو PDF رسمي
- ✅ لم تُنشأ أي ملفات JSON أو XLSX أو JSONL

---

## 18. نتائج التحقق

- **make validate:** PASS ✓
- **make test:** 2488 passed (9 pre-existing failures in chinese_remediation tests — same as on main before this PR) ✓

---

## 19. الحدود القانونية وتشغيل المنتج

- النص العربي الرسمي هو المصدر الحاكم
- ليست استشارة قانونية
- ليست ترجمة رسمية
- لا تفسير قانوني
- لا استنتاجات قانونية مولّدة
- لا حكم على الصحة القانونية
- لا تحقق دلالي
- السجلات الإنجليزية مرجعية فقط
- الترجمة الإنجليزية الرسمية هي مرجع مساعد فقط
- السجلات الصينية مرجع داخلي فقط
- لا محاذاة ثلاثية اللغات
- لا ادعاء إصدار عام
- لا RAG / لا LLM / لا API / لا شبكة / لا ترميزات / لا واجهة
- repository-owner legal review active; external legal review optional for enterprise/official adoption

---

## 20. المرحلة التالية المُوصى بها

**LABOR_LAW_ARTICLE_2_DEFINITIONS_AND_EXTRACTION_ISSUES_POPULATION_001**