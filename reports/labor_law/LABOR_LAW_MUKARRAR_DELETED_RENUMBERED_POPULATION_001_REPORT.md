# تقرير مرحلة تتبع المكرر والمحذوف والمعاد ترقيمه — نظام العمل

## 1. اسم المرحلة والخط الأساسي
- **المرحلة:** LABOR_LAW_MUKARRAR_DELETED_RENUMBERED_POPULATION_001
- **الخط الأساسي:** 3ab61353b2a1fbda108515e4f001f15856442509

## 2. الفرع
- **الفرع:** glm/labor-law-mukarrar-deleted-renumbered-population-001

## 3. الملفات المعدلة/المنشأة

### ملفات معدلة:
1. `worksheets/labor_law/reconciliation_scaffold/mukarrar_deleted_renumbered_tracking.csv` — تعبئة كاملة (42 صفاً)
2. `worksheets/labor_law/reconciliation_scaffold/article_inventory.csv` — تحديث الأعلام الهيكلية (35 صفاً محدثاً)
3. `worksheets/labor_law/reconciliation_scaffold/extraction_quality_issues.csv` — توسيع من 10 إلى 45 صفاً
4. `worksheets/labor_law/reconciliation_scaffold/unresolved_issues_log.csv` — توسيع من 9 إلى 43 مسألة
5. `worksheets/labor_law/reconciliation_scaffold/readiness_summary.csv` — تحديث الملخص

### ملفات منشأة:
1. `reports/labor_law/LABOR_LAW_MUKARRAR_DELETED_RENUMBERED_POPULATION_001_REPORT.md` — هذا التقرير

## 4. المصدر المستخدم
- المصدر الرسمي العربي: بوابة الأنظمة السعودية (laws.boe.gov.sa)
- رابط القانون: https://laws.boe.gov.sa/boelaws/laws/lawdetails/08381293-6388-48e2-8ad2-a9a700f2aa94/1
- ملفات تتبع التعديلات السابقة: amendment_tracking.csv (127 صفاً)
- جرد المقالات السابق: article_inventory.csv (247 صفاً)

## 5. المنهجية المستخدمة
1. تحليل amendment_tracking.csv لاستخراج المقالات المؤكدة هيكلياً كمكرر أو محذوف/ملغى أو معاد ترقيمه
2. مطابقة المقالات المؤكدة كمكرر (79، 229) من article_inventory.csv
3. تحديد المقالات غير المستقلة كمكرر (11، 131) من amendment_tracking
4. تحديد المقالات المعاد ترقيمها (231/240، 232/242) من article_inventory + amendment_tracking
5. تحديد المقالات المكررة في BOE (233/234/235) من المرحلة السابقة
6. استخراج 30 مقالاً محذوفاً/ملغى من amendment_tracking (article_abolished_by_amendment و article_deleted_by_amendment)
7. استخراج 3 مقالات معاد ترقيمها من amendment_tracking (35، 58، 178 عبر M/44)
8. تحديث article_inventory.csv بالأعلام الهيكلية المناسبة
9. استخدام حالات عدم اليقين المضبوطة للقضايا غير المؤكدة

## 6. عدد صفوف mukarrar_deleted_renumbered_tracking
- **42 صفاً** (بعد رأس الجدول)

## 7. عدد المكرر المؤكد
- **2 مقالات** (المادة 79 مكرر، المادة 229 مكرر)
- كلاهما موجود كمادة مستقلة في BOE وفي article_inventory

## 8. عدد المكرر الممكن/غير المؤكد
- **2 مقالات** (المادة 11، المادة 131)
- لم يتم العثور عليهما كمادة مستقلة في BOE
- amendment_tracking يؤكد إضافة مكرر عبر التعديل (mukarrar_added_by_amendment)
- الحالة: MUKARRAR_NOT_INDEPENDENT_ITEM / NEEDS_MANUAL_REVIEW

## 9. عدد المحذوف/الملغى المؤكد
- **30 مقالاً** مؤكد هيكلياً من amendment_tracking:
  - المادة 78 (abolished)
  - المادتان 149، 150 (deleted via M/5)
  - المادة 156 (abolished via M/134)
  - المقالات 195، 197، 203، 205، 206، 207، 208 (abolished via M/44)
  - المقالات 210–228 (abolished via 22/1/1435)

## 10. عدد المعاد ترقيمه المؤكد
- **5 مقالات:**
  - المادة 231 (معاد ترقيمها من 240) — من article_inventory
  - المادة 232 (معاد ترقيمها من 242) — من article_inventory
  - المادة 35 (معاد ترقيمها عبر M/44) — من amendment_tracking
  - المادة 58 (معاد ترقيمها) — من amendment_tracking
  - المادة 178 (معاد ترقيمها عبر M/44) — من amendment_tracking

## 11. عدد شذوذ البنية المزدوجة/المصدر
- **3 مقالات** (233، 234، 235) — عناصر BOE مكررة
- تم إزالة التكرار في المرحلة السابقة
- الحالة: DUPLICATE_BOE_ITEM / CONFIRMED_STRUCTURAL_ONLY

## 12. ملخص تحديث extraction_quality_issues
- **من 10 إلى 45 صفاً**
- الصفوف الأصلية (eqi_001–eqi_010) محفوظة ومحسّنة
- صفوف جديدة:
  - eqi_011–012: تأكيد المكرر المستقل (79، 229)
  - eqi_013–015: مقالات معاد ترقيمها (35، 58، 178)
  - eqi_016–045: مقالات محذوفة/ملغاة (30 مقالاً)
- أنواع المسائل: MUKARRAR_CONFIRMED_STRUCTURAL_ONLY، RENUMBERED_ENTRY_NEEDS_HANDLING، DELETED_OR_ABOLISHED_NEEDS_CHECK

## 13. عدد صفوف unresolved_issues_log
- **43 مسألة** (من 9 في المرحلة السابقة)
- المسائل الأصلية (issue_001–009) محفوظة ومحسّنة
- مسائل جديدة:
  - issue_011–013: مقالات معاد ترقيمها (35، 58، 178)
  - issue_014–043: مقالات محذوفة/ملغاة (30 مقالاً)
- جميعها non-blocking، owner_decision_needed=no

## 14. ملخص تحديث article_inventory
- **247 صفاً محفوظاً** (لا تغيير في العدد)
- **35 صفاً محدثاً:**
  - 30 مقالاً: deleted_or_abolished_flag = yes + reviewer_notes محدث
  - 2 مقالاً (11، 131): unresolved_issue_flag = needs_manual_check + reviewer_notes محدث
  - 3 مقالات (35، 58، 178): unresolved_issue_flag = needs_manual_check + reviewer_notes محدث
- لم يتم تغيير أي نص قانوني
- لم يتم تغيير أي رابط مصدر

## 15. نتيجة readiness_summary
- total_articles: 247
- total_amended_articles: 106
- total_m44_related_articles: 45
- total_mukarrar_articles: 2 (المؤكدة كمادة مستقلة: 79، 229)
- total_deleted_or_abolished_articles: 30 (مؤكدة هيكلياً)
- total_renumbered_articles: 5 (231، 232، 35، 58، 178)
- total_unresolved_issues: 43
- ingestion_readiness_decision: NOT_READY
- summary_notes: تتبع هيكلي للمكرر/المحذوف/المعاد ترقيمه فقط؛ لا نسخ نص قانوني؛ لا مصالحة؛ لا استيعاب

## 16. المسائل غير المحلولة المنقولة
1. المادة 11 مكرر — غير موجود كمادة مستقلة في BOE
2. المادة 131 مكرر — غير موجود كمادة مستقلة في BOE
3. المادة 231/240 معاد ترقيمها — يحتاج معالجة لاحقاً
4. المادة 232/242 معاد ترقيمها — يحتاج معالجة لاحقاً
5. المقالات 233/234/235 مكررة في BOE — تم إزالة التكرار
6. 30 مقالاً محذوفاً/ملغى — يحتاج مصالحة نصية لاحقة
7. 3 مقالات معاد ترقيمها (35، 58، 178) — يحتاج معالجة لاحقة
8. تباين عدد M/44 (45 BOE مقابل 47 سابقاً)
9. تباين عدد التعديلات (106 BOE مقابل 104 سابقاً)
10. بعض ملاحظات التعديل بلا رقم مرسوم

## 17. ما لم يتم تعبئته عمداً
- لم يتم نسخ أي نص قانوني من BOE
- لم يتم إنشاء سجلات مقالات (article corpus records)
- لم يتم إجراء أي مصالحة نصية
- لم يتم تحديد المادة 11 و 131 كمادة مستقلة في article_inventory (لعدم وجودها كعنصر مستقل)
- لم يتم إنشاء سجلات إنجليزية
- لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة
- لم يتم إنشاء JSON/JSONL/XLSX/PDF
- لم يتم تأكيد حالات المحذوف/الملغى غير المؤكدة هيكلياً

## 18. تأكيد عدم نسخ نص قانوني
- **مؤكد:** لم يتم نسخ أي نص قانوني عربي من المصدر الرسمي
- **مؤكد:** لم يتم نسخ أي نص إنجليزي من الترجمة الرسمية
- جميع الملاحظات في CSV هي ملاحظات هيكلية قصيرة فقط

## 19. تأكيد عدم إجراء المصالحة
- **مؤكد:** لم يتم إجراء أي مصالحة نصية
- جميع الصفوف تحمل حالة CARRIED_FORWARD أو STRUCTURAL_ONLY

## 20. تأكيد عدم استيعاب نظام العمل
- **مؤكد:** لم يحدث أي استيعاب (ingestion) لنظام العمل
- ingestion_readiness_decision = NOT_READY

## 21. تأكيد عدم إنشاء سجلات إنجليزية أو محاذاة
- **مؤكد:** لم يتم إنشاء سجلات إنجليزية
- **مؤكد:** لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة
- السجلات الإنجليزية تبقى مرجعاً فقط
- الترجمة الإنجليزية الرسمية تبقى دعماً مرجعياً فقط
- السجلات الصينية تبقى مرجعاً داخلياً فقط

## 22. تأكيد عدم تضمين ملفات مصدر/PDF/TXT/HTML
- **مؤكد:** لم يتم تضمين أي ملفات مصدر
- **مؤكد:** لم يتم تضمين أي PDF أو TXT أو HTML رسمي
- **مؤكد:** لم يتم تضمين أي ملفات محملة سابقاً

## 23. نتائج التحقق
- `make validate` → **PASS** (ALL CHECKS PASSED ✓)
- `make test` → **9 فشائل سابقة (chinese_remediation)** — لا فشائل جديدة
- إجمالي الاختبارات: 2492 (2483 ناجح + 9 فشل سابق)
- لا تغيير في عدد الفشائل مقارنة بالخط الأساسي

## 24. الحدود القانونية/المنتجية
- المصدر العربي الرسمي يحكم
- لا يُعد نصيحة قانونية
- لا يُعد ترجمة رسمية
- لا يوجد تفسير قانوني
- لا توجد استنتاجات قانونية مولّدة
- لا يوجد حكم على الصحة القانونية
- لا يوجد تحقق دلالي
- السجلات الإنجليزية مرجعية فقط
- الترجمة الإنجليزية الرسمية دعم مرجعي فقط
- السجلات الصينية مرجع داخلي فقط
- لا توجد محاذاة ثلاثية اللغة
- لا ادعاء بإصدار عام
- لا RAG/LLM/API/network/embeddings/UI
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 25. المرحلة الموصى بها التالية
- **LABOR_LAW_TEXT_RECONCILIATION_BATCH_001_ARTICLES_001_025**