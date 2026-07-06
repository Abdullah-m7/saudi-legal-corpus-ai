# تقرير: أساس البحث المعجمي المحلي للمدونة القانونية السعودية

## المرحلة: CORPUS_LOCAL_LEXICAL_SEARCH_FOUNDATION

**المستودع:** al3obdi/saudi-legal-corpus-ai
**الفرع:** glm/corpus-local-lexical-search-foundation
**التاريخ:** 2026-07-06

---

## 1. نظرة عامة

إنشاء أداة بحث معجمي محلية خفيفة تعمل على سجلات التصدير العربية الحاكمة (450 سجل). البحث حتمي، يعمل دون اتصال بالشبكة، ولا يستخدم تضمينات أو قواعد بيانات شعاعية أو نماذج لغوية أو واجهات برمجية.

هذا ليس نظام استرجاع معزز (RAG). ليس استشارة قانونية. ليس ترجمة رسمية. النص العربي الرسمي هو الحاكم.

## 2. نطاق البحث

- **المصدر:** data/exports/v1/primary_arabic_governing_records.jsonl
- **السجلات القابلة للبحث:** 450 سجل عربي حاكم
- **حقول البحث:** text_ar، title_ar، article_ordinal_ar
- **السجلات المُستبعدة:** الإنجليزية، الصينية، تدقيق الإغلاق

## 3. سلوك البحث

- مطابقة العبارة الدقيقة: وزن أعلى
- مطابقة جميع المصطلحات: مكافأة إضافية
- مطابقة العنوان: مكافأة إضافية
- تطبيع عربي خفيف للبحث فقط (لا يغير النص المخزن):
  - إزالة التطويل
  - توحيد أشكال الألف
  - توحيد الياء
  - توحيد التاء المربوطة
  - إزالة التشكيل
- الترتيب حتمي: نفس الاستعلام يعيد نفس النتائج
- كسر التعادل: حسب export_record_id تصاعديًا

## 4. واجهة سطر الأوامر

```bash
python3 scripts/search_primary_arabic_export.py "الشركة"
python3 scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 10
python3 scripts/search_primary_arabic_export.py "التصفية" --track companies_law
python3 scripts/search_primary_arabic_export.py "الجمعية العامة" --json
```

## 5. الحدود القانونية

- النص العربي الرسمي هو الحاكم: مؤكد
- ليس ترجمة رسمية: مؤكد
- ليس استشارة قانونية: مؤكد
- لا تفسير قانوني أو استنتاجات: مؤكد
- لا سجلات إنجليزية: مؤكد
- لا سجلات صينية: مؤكد
- لا محاذاة ثلاثية اللغات: مؤكد
- لا إصدار علني: مؤكد
- لا تضمينات أو قواعد شعاعية أو واجهات برمجية أو شبكة: مؤكد

## 6. الملفات المُضافة

1. `scripts/search_primary_arabic_export.py` — أداة بحث سطر الأوامر
2. `scripts/validate_corpus_local_search.py` — مُدقق للقراءة فقط (29 فحص)
3. `tests/test_corpus_local_search.py` — مجموعة اختبارات
4. `docs/CORPUS_LOCAL_SEARCH.md` — دليل الاستخدام
5. `reports/corpus_search/CORPUS_LOCAL_LEXICAL_SEARCH_FOUNDATION_AR.md` — هذا التقرير
6. `reports/corpus_search/CORPUS_LOCAL_LEXICAL_SEARCH_FOUNDATION_REPORT.txt` — تقرير نصي

## 7. الملفات المُعدَّلة

1. `Makefile` — إضافة هدفَي تحقق وتجربة
2. `README.md` — إضافة موجز
3. `STATUS.md` — إضافة موجز

## 8. التحقق

- `make validate`: نجاح
- `make test`: 2231 نجاح
- `make corpus-registry-validate`: نجاح (22/22)
- `make corpus-export-primary-arabic-validate`: نجاح (43/43)
- `make corpus-local-search-validate`: نجاح (29/29)

## 9. النتيجة النهالية

نجاح — أساس البحث المعجمي المحلي جاهز. 450 سجل عربي قابل للبحث. حتمي، يعمل دون اتصال، لا يعتمد على تضمينات أو شبكة.