# تقرير: تأسيس حزمة عرض مشغل استرجاع السجل القانوني السعودي

## المرحلة

CORPUS_RETRIEVAL_OPERATOR_DEMO_PACK_FOUNDATION

## النتيجة

APPLY — تم التنفيذ كحزمة توثيق مشغل محلية

## تأكيد خط الأساس

- المرجع: main @ eaddea5214c3b9cfcc1e1376751828cd08497179
- الفرع: glm/corpus-retrieval-operator-demo-pack-foundation

## سلسلة التحقق

### ١. فحص ملاءمة الرؤية
- يجعل سير العمل الحالي أسهل للتشغيل والعرض: نعم
- يقلل الارتباك لدى المشغل: نعم
- يتجنب إضافة منطق جديد غير ضروري: نعم

### ٢. فحص الحد القانوني
- المصدر العربي الرسمي يحكم: مؤكد
- ليست استشارة قانونية: مؤكد
- ليست ترجمة رسمية: مؤكد
- لا تفسير قانوني: مؤكد
- لا استنتاجات قانونية مولدة: مؤكد
- لا حكم على الصحة القانونية: مؤكد
- لا تحقق الدعم الدلالي: مؤكد
- لا استدعاء LLM: مؤكد
- لا توليد إجابات: مؤكد
- لا سجلات إنجليزية: مؤكد
- لا سجلات صينية: مؤكد
- لا محاذاة ثلاثية اللغة: مؤكد
- لا إصدار عام: مؤكد

### ٣. فحص انضباط النطاق
- استخدام سير العمل الحالي وسيناريوهات العرض: مؤكد
- عدم تعديل primary_arabic_governing_records.jsonl: مؤكد
- عدم تعديل ملفات السجل المصدرية: مؤكد
- عدم تعديل official_text_ar: مؤكد
- عدم تعديل ترتيب البحث: مؤكد
- عدم إضافة RAG/تضمينات/دلالي/API/واجهة/قاعدة/شبكة: مؤكد
- عدم الالتزام بمخرجات سير العمل المولدة: مؤكد

### ٤. فحص مضاد للهندسة الزائدة
- عدم إنشاء تطبيق عرض كامل: مؤكد
- عدم إضافة لقطات شاشة/شرائح/فيديوهات/صفحات ويب: مؤكد
- عدم إضافة إطار عمل جديد: مؤكد
- ملفات قصيرة ومركزة على المشغل: مؤكد
- توثيق وتحقق بسيط فقط: مؤكد

### ٥. فحص قيمة المنتج/الأتمتة
- المشغل يستطيع تشغيل عرض في أقل من بضعة أوامر: مؤكد
- المشغل يعرف ما يعرضه وما لا يدعيه: مؤكد
- المشغل يستطيع التحقق من الجاهزية قبل العرض: مؤكد
- المشغل لديه سكربت بروفة موجز: مؤكد
- المخرجات المولدة تبقى خارج المستودع: مؤكد

## نطاق حزمة عرض المشغل

حزمة توثيق مشغل محلية موجزة لسير عمل استرجاع العرض التوضيحي. خمسة ملفات عربية + مدقق + اختبارات. لا LLM، لا RAG، لا تضمينات، لا API، لا شبكة، لا مخرجات مولدة ملتزمة.

## الملفات المضافة

١. docs/operator_demo_pack/START_HERE_AR.md
٢. docs/operator_demo_pack/DEMO_SCRIPT_AR.md
٣. docs/operator_demo_pack/REHEARSAL_CHECKLIST_AR.md
٤. docs/operator_demo_pack/COMMANDS_AR.md
٥. docs/operator_demo_pack/BOUNDARIES_AR.md
٦. scripts/validate_operator_demo_pack.py
٧. tests/test_operator_demo_pack.py
٨. reports/corpus_search/CORPUS_RETRIEVAL_OPERATOR_DEMO_PACK_FOUNDATION_AR.md
٩. reports/corpus_search/CORPUS_RETRIEVAL_OPERATOR_DEMO_PACK_FOUNDATION_REPORT.txt

## الملفات المعدلة

١. Makefile (أهداف validate + smoke)
٢. README.md (وصف حزمة عرض المشغل)
٣. STATUS.md (إدخال حزمة عرض المشغل)

## الأوامر المشمولة

- make validate
- make corpus-retrieval-demo-scenarios-validate
- make corpus-retrieval-demo-scenarios-smoke
- make corpus-retrieval-operator-demo-pack-validate
- python3 scripts/run_retrieval_demo_scenarios.py
- python3 scripts/run_retrieval_demo_scenarios.py --output-dir /tmp/my_demo
- python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" (بحث عام)
- python3 scripts/run_retrieval_workflow.py "التصفية" --track companies_law (مرشح مسار)
- python3 scripts/run_retrieval_workflow.py "نموذج" --record-type form (مرشح نوع)
- python3 scripts/run_retrieval_workflow.py "الجمعية العامة" --prompt-mode cautious_answer_draft
- python3 scripts/run_retrieval_workflow.py "التوكيل" --record-type appendix --include-full-text

## الحدود

- المصدر العربي الرسمي يحكم
- ليست استشارة قانونية
- ليست ترجمة رسمية
- لا تفسير قانوني
- لا استنتاجات قانونية مولدة
- لا حكم على الصحة القانونية
- لا تحقق الدعم الدلالي
- لا استدعاء LLM
- لا RAG
- لا إصدار عام
- مراجعة قانونية من مالك المستودع نشطة؛ المراجعة القانونية الخارجية اختيارية للاعتماد المؤسسي أو الرسمي

## سياسة المخرجات المولدة

- جميع مخرجات سير العمل في أدلة مؤقتة فقط
- لا مخرجات مولدة ملتزمة في المستودع
- دليل docs/operator_demo_pack/ يحتوي فقط على ملفات markdown
- لا حزم سياق أو حزم طلب ملتزمة

## النظافة

- لا لقطات شاشة/شرائح/واجهة ويب/API: مؤكد
- لا استدعاء LLM: مؤكد
- لا إجابات قانونية مولدة: مؤكد
- لا نسب لكاتب/أداة/نموذج: مؤكد
- شجرة العمل نظيفة: مؤكد