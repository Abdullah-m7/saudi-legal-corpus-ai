# تقرير مرحلة مشغّل تطابق نظام العمل — Operator V1

## 1. المرحلة والخط الأساسي

- **المرحلة:** LABOR_LAW_RECONCILIATION_OPERATOR_V1
- **الخط الأساسي المستهدف:** بعد دمج PR #120 على `main`، أي `c786d9dfbf73fb7e90677c73e0908e242758b7ec`

## 2. الغرض

إنشاء حزمة تشغيل قابلة لإعادة الاستخدام لتقليل حجم بروموتات الدفعات القادمة، وتثبيت القواعد المتكررة، وإضافة فاحص هيكلي محلي يمنع الأخطاء التشغيلية قبل فتح PR أو الدمج.

## 3. الملفات المنشأة

1. `docs/labor_law_reconciliation/OPERATOR_RULES.md`
2. `docs/labor_law_reconciliation/BATCH_EXECUTION_GUIDE.md`
3. `docs/labor_law_reconciliation/BATCH_REPORT_REQUIREMENTS.md`
4. `worksheets/labor_law/reconciliation_scaffold/batch_execution_manifest.csv`
5. `tools/check_labor_law_reconciliation_batch.py`
6. `reports/labor_law/LABOR_LAW_RECONCILIATION_OPERATOR_V1_REPORT.md`

## 4. الملفات المعدلة

لا توجد ملفات بيانات أو نصوص قانونية معدلة في هذه المرحلة.

## 5. قدرات الفاحص المحلي

الفاحص `tools/check_labor_law_reconciliation_batch.py` يتحقق من الآتي:

- وجود ملف CSV الخاص بالدفعة.
- تطابق عدد صفوف الدفعة مع النطاق المتوقع.
- عدم تكرار `article_key`.
- أن الصفوف النظيفة تحتوي نصًا وهاشًا وطولًا موجبًا وحالة جاهزية صحيحة.
- أن الصفوف المعدلة/المنبثقة لا تحتوي نصًا ملتقطًا ولا هاشًا وطولها صفر.
- أن المواد الملغاة/المحذوفة لا تحتوي نصًا قديمًا ملتقطًا كنص حالي.
- أن `readiness_summary.total_unresolved_issues` يساوي عدد صفوف `unresolved_issues_log.csv`.
- أن عداد القضايا غير المحلولة لا ينخفض تحت floor محدد.
- أن التقرير لا يحتوي عبارات تحقق مؤجلة.
- أن التقرير يحتوي نتائج `make validate` و`make test` الفعلية.
- أن حدود المنتج والقانون مضبوطة.

## 6. أمر الفحص المقترح

```bash
python tools/check_labor_law_reconciliation_batch.py --batch 006 --range 126-150 --unresolved-floor 91
```

## 7. ما لم يتم تنفيذه

- لم يتم تعديل أي نص قانوني.
- لم يتم إنشاء سجلات نهائية للمواد.
- لم يتم إدخال نظام العمل في السجل النهائي.
- لم يتم تعديل registry أو export records أو runtime أو validators.
- لم يتم إنشاء سجلات إنجليزية.
- لم يتم إنشاء محاذاة ثنائية أو ثلاثية اللغة.
- لم يتم إنشاء RAG أو UI أو API أو network أو embeddings.
- لم يتم إنشاء ملفات JSON/JSONL/XLSX/PDF أو source dumps.

## 8. التحقق

هذه الحزمة أُعدت كحزمة تطبيق/PR. يجب تشغيل الأوامر التالية بعد تطبيقها على فرع فعلي داخل المستودع:

```bash
make validate
make test
python tools/check_labor_law_reconciliation_batch.py --batch 006 --range 126-150 --unresolved-floor 91
```

## 9. الحدود القانونية والمنتجية

- المصدر العربي الرسمي هو الحاكم.
- هذا ليس استشارة قانونية.
- هذا ليس ترجمة رسمية.
- لا تفسير قانوني.
- لا استنتاجات قانونية مولدة.
- لا حكم على الصحة القانونية.
- السجلات الإنجليزية مرجعية فقط.
- الترجمة الإنجليزية الرسمية دعم مرجعي فقط.
- السجلات الصينية مرجع داخلي فقط.
- لا محاذاة ثلاثية اللغة.
- لا ادعاء إصدار عام.
- لا RAG/LLM/API/network/embeddings/UI.
- repository-owner legal review active; external legal review optional for enterprise/official adoption

## 10. المرحلة التالية بعد تطبيق هذه الحزمة

`LABOR_LAW_TEXT_RECONCILIATION_BATCH_007_ARTICLES_151_175_WITH_AMENDMENT_POPUP_HANDLING`
