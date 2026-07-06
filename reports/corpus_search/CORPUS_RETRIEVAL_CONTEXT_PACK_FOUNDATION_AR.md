# تقرير: تأسيس حزمة سياق الاسترجاع — مرحلة التأسيس

## المرحلة

تأسيس حزمة سياق الاسترجاع (Retrieval Context Pack Foundation)

## النتيجة

تم بنجاح ✓

## الأساس المؤكد

الفرع الرئيسي (main) عند:
`0a64e79c22a76733adee5e713fc6a0abd60d647d`

## الفرع

`glm/corpus-retrieval-context-pack-foundation`

## تحليل المناقشة متعدد الوكلاء (Multi-Agent Tree Debate)

### 1. المهندس القانوني (Legal Architect)
- ✓ لا يولد إجابات قانونية.
- ✓ لا يفسّر أو يلخّص أو يستنتج.
- ✓ يكتفي بتغليف السجلات العربية الحاكمة المسترجعة.
- ✓ المصدر العربي الرسمي يبقى حاكمًا.
- ✓ لا تُستخدم سجلات إنجليزية أو صينية.
- ✓ لا ادعاء لإصدار عام.

### 2. مهندس البيانات والأتمتة (Data/Automation Engineer)
- ✓ الحزمة حتمية (deterministic) وتعمل دون اتصال بالشبكة.
- ✓ تقرأ من ملف JSONL المُصدَّر وأداة البحث المحلية فقط.
- ✓ لا تضمينات (embeddings) ولا قاعدة بيانات شعاعية ولا واجهة برمجية ولا شبكة ولا استدعاءات نماذج لغوية.
- ✓ مخطط الإخراج مستقر وقابل للاختبار.

### 3. راغب البراغماتي/المنتج (Product/RAG Pragmatist)
- ✓ هذه هي الجسر الصحيح بين البحث المحلي وبين RAG المستقبلي.
- ✓ حزم السياق مفيدة لضمان الجودة وبناء الإشارات والمراجعة واختبار الاسترجاع.
- ✓ مخرجات JSON وMarkdown كلاهما مفيد.

### 4. محامي الشيطان (Devil's Advocate)
- تم التحقق: هذا ليس مبكرًا — البحث المحلي موجود والجاهزية مكتملة.
- تم رفض: توليد الإجابات، التلخيص، إعادة الترتيب الدلالي، التضمينات، الواجهة البرمجية.
- النتيجة: تغليف فقط، لا استدلال.

### 5. محامي السرعة (Founder-Speed Advocate)
- ✓ أداة عملية تم شحنها الآن.
- ✓ بسيطة ومرئية: واجهة سطر أوامر واحدة، مُتحقق واحد، ملف اختبار واحد، مستند واحد، تقرير واحد.
- ✓ لا تقسيم مفرط.

### القرار النهائي للمناقشة

**تطبيق (APPLY)** — مع الالتزام بأن يكون تغليف سياق حتمي فقط.

## سلسلة التحقق (Chain of Verification)

### 1. فحص ملاءمة الرؤية
- ✓ يجعل مخرجات البحث أكثر قابلية للاستخدام.
- ✓ يجسر نحو RAG دون بناء RAG.
- ✓ يدعم المراجعة وضمان الجودة وبناء الإشارات.

### 2. فحص الحدود القانونية
- ✓ المصدر العربي الرسمي حاكم.
- ✓ ليست نصيحة قانونية.
- ✓ ليست ترجمة رسمية.
- ✓ لا تفسير قانوني.
- ✓ لا استنتاجات قانونية مولّدة.
- ✓ لا تلخيص إلا تسميات بيانات وصفية موجودة مسبقًا.
- ✓ لا سجلات إنجليزية.
- ✓ لا سجلات صينية.
- ✓ لا محاذاة ثلاثية اللغة.
- ✓ لا إصدار عام.

### 3. فحص انضباط النطاق
- ✓ يقرأ من `primary_arabic_governing_records.jsonl` وأداة/دوال البحث المحلية فقط.
- ✓ لا يعدّل ملف JSONL المُصدَّر.
- ✓ لا يعدّل ملفات المدونة المصدرية.
- ✓ لا يعدّل `official_text_ar`.
- ✓ لا يغيّر ترتيب البحث إلا عند الضرورة لاستيراد دالة قابلة لإعادة الاستخدام.
- ✓ لا يضيف RAG أو تضمينات أو بحث دلالي أو واجهة برمجية أو واجهة مستخدم أو قاعدة بيانات أو شبكة.

### 4. فحص مكافحة الهندسة المفرطة
- ✓ لا إطار استرجاع ضخم.
- ✓ لا خطوط أنابيب متعددة المراحل.
- ✓ لا مخططات معقدة.
- ✓ لا إشارات نماذج لغوية للإجابة.
- ✓ مخطط حزمة سياق واحد (v1).

### 5. فحص قيمة المنتج/الأتمتة
- ✓ حزمة السياق سهلة الفحص.
- ✓ قابلة للقراءة آليًا.
- ✓ تتضمن مصدرًا كافيًا للوثوق بالسجلات المسترجعة.
- ✓ قابلة لإعادة الاستخدام لمراحل RAG/الإشارات/التقييم المستقبلية.

## نطاق حزمة السياق

مولّد حزم سياق استرجاع محلي حتمي:
- يأخذ استعلامًا
- يشغّل البحث المعجمي المحلي الموجود
- يصدّر أفضل النتائج كحزمة سياق/أدلة منظمة (JSON أو Markdown)

## البيانات المصدرية

- ملف: `data/exports/v1/primary_arabic_governing_records.jsonl`
- عدد السجلات: 450
- المسارات: companies_law, implementing_regulations_general, implementing_regulations_listed_joint_stock
- أنواع السجلات: article, form, appendix
- اللغة: ar (العربية فقط)
- الصفة الحاكمة: arabic_governing_text

## السجلات المضمّنة

- سجلات نظام الشركات (companies_law): 281 مادة
- اللوائح التنفيذية العامة (implementing_regulations_general): 95 مادة + 4 ملاحق/نماذج
- لوائح الشركات المساهمة المدرجة (implementing_regulations_listed_joint_stock): 69 مادة + 1 ملحق

## السجلات المستبعدة

- السجلات الإنجليزية (جميعها)
- السجلات الصينية (جميعها)
- المحاذاة ثلاثية اللغة
- أي سجلات غير حاكمة
- أي سجلات من مسارات غير عربية

## أمثلة واجهة سطر الأوامر

```bash
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة"
python3 scripts/build_retrieval_context_pack.py "الجمعية العامة" --limit 5
python3 scripts/build_retrieval_context_pack.py "التصفية" --track companies_law --limit 5
python3 scripts/build_retrieval_context_pack.py "التوكيل" --record-type appendix --limit 3
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --format json
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --format markdown
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --output /tmp/context_pack.json
python3 scripts/build_retrieval_context_pack.py "مجلس الإدارة" --include-full-text --limit 3
```

## مخطط إخراج JSON

مستوى أعلى: pack_version, query, normalized_query, generated_at_date, source_search_tool, source_export_file, source_export_record_count, retrieval_method, limit, filters, total_matches, returned, legal_boundaries, records

لكل سجل: rank, score, export_record_id, source_track_id, source_record_id, corpus_family, document_type, record_type, language, governing_status, title_ar, article_number/record_number, snippet, text_ar (اختياري), source_url, source_authority, publication_date_hijri, publication_date_gregorian, source_data_path, source_text_sha256

## سلوك Markdown

- تخطيط عربي مناسب (RTL)
- عنوان يتضمن الاستعلام وعدد النتائج
- قسم الحدود القانونية
- قسم البيانات الوصفية
- قائمة مرقمة بالسجلات المسترجعة
- النص الكامل فقط عند تمرير `--include-full-text`

## الحدود القانونية

- المصدر العربي الرسمي حاكم
- ليست نصيحة قانونية
- ليست ترجمة رسمية
- لا تفسير قانوني
- لا استنتاجات قانونية مولّدة
- لا سجلات إنجليزية/صينية
- لا محاذاة ثلاثية اللغة
- لا إصدار عام

## الملفات المضافة

1. `scripts/build_retrieval_context_pack.py` — باني حزم السياق
2. `scripts/validate_retrieval_context_pack.py` — مُتحقق للقراءة فقط
3. `tests/test_retrieval_context_pack.py` — 43 اختبار
4. `docs/CORPUS_RETRIEVAL_CONTEXT_PACK.md` — دليل الاستخدام
5. `reports/corpus_search/CORPUS_RETRIEVAL_CONTEXT_PACK_FOUNDATION_AR.md` — هذا التقرير
6. `reports/corpus_search/CORPUS_RETRIEVAL_CONTEXT_PACK_FOUNDATION_REPORT.txt` — التقرير النصي

## الملفات المعدّلة

- `Makefile` — إضافة هدفَي `corpus-retrieval-context-pack-validate` و `corpus-retrieval-context-pack-smoke`
- `README.md` — إضافة قسم حزم سياق الاسترجاع
- `STATUS.md` — إضافة قسم حزم سياق الاسترجاع

## نتائج التحقق

- المُتحقق: 41 فحص، جميعها نجحت ✓
- الاختبارات: 43 اختبار، جميعها نجحت ✓
- تسلسل التحقق الكامل: نجح ✓

## النظافة

- لا إسناد إلى مولّد/جلسة/مؤلف مشارك/أداة/نموذج
- لا تعديل لملفات المصدر
- لا إخراج ثابت مُلتزم به (إلا إذا احتاج المُتحقق ثابتًا ثابتًا)
- حتمية كاملة لنفس الاستعلام
- لا شبكة، لا واجهة برمجية، لا تضمينات