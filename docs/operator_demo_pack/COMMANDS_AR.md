# الأوامر المحلية — حزمة عرض المشغل

جميع الأوامر قابلة للنسخ واللصق. تعمل محليًا بدون شبكة.

## التحقق

```bash
# التحقق العام
make validate

# التحقق من سيناريوهات العرض
make corpus-retrieval-demo-scenarios-validate

# التحقق من حزمة عرض المشغل
make corpus-retrieval-operator-demo-pack-validate
```

## اختبار الدخان (Smoke)

```bash
# تشغيل جميع السيناريوهات الستة + أمر يدوي + تأكيد عدم التزام
make corpus-retrieval-demo-scenarios-smoke
```

## تشغيل السيناريوهات

```bash
# تشغيل جميع السيناريوهات في دليل مؤقت
python3 scripts/run_retrieval_demo_scenarios.py

# تشغيل جميع السيناريوهات في دليل محدد
python3 scripts/run_retrieval_demo_scenarios.py --output-dir /tmp/my_demo
```

## أوامر سير عمل يدوية

### مجلس الإدارة (بحث عام)

```bash
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode prepare_prompt --limit 3 --prompt-mode evidence_brief \
  --formats both --output-dir /tmp/corpus_demo_board
```

### التصفية (مرشح مسار نظام الشركات)

```bash
python3 scripts/run_retrieval_workflow.py "التصفية" \
  --track companies_law --mode prepare_prompt --limit 3 \
  --prompt-mode evidence_brief --formats both \
  --output-dir /tmp/corpus_demo_liquidation
```

### نموذج (مرشح نوع السجل: نموذج)

```bash
python3 scripts/run_retrieval_workflow.py "نموذج" \
  --record-type form --mode prepare_prompt --limit 3 \
  --prompt-mode evidence_brief --formats both \
  --output-dir /tmp/corpus_demo_forms
```

### الجمعية العامة (قالب إجابة حذرة)

```bash
python3 scripts/run_retrieval_workflow.py "الجمعية العامة" \
  --mode prepare_prompt --limit 3 --prompt-mode cautious_answer_draft \
  --formats both --output-dir /tmp/corpus_demo_assembly
```

### التوكيل (ملحق، نص كامل)

```bash
python3 scripts/run_retrieval_workflow.py "التوكيل" \
  --record-type appendix --mode prepare_prompt --limit 1 \
  --prompt-mode evidence_brief --include-full-text \
  --formats both --output-dir /tmp/corpus_demo_proxy
```

## فحص الاستشهادات (وضع check_draft)

```bash
# تجهيز حزمة طلب
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode prepare_prompt --limit 3 --formats json \
  --output-dir /tmp/corpus_demo_citation

# كتابة مسودة اختبار
python3 -c "import json; pack=json.load(open('/tmp/corpus_demo_citation/prompt_pack.json')); rid=pack['retrieved_records'][0]['export_record_id']; open('/tmp/draft.md','w').write('هذه إجابة معلوماتية وليست استشارة قانونية للمراجعة القانونية [[export_record_id='+rid+']].\n\nوفقًا للنظام [[export_record_id='+rid+']].\n')"

# فحص المسودة
python3 scripts/run_retrieval_workflow.py "مجلس الإدارة" \
  --mode check_draft --limit 3 --prompt-mode cautious_answer_draft \
  --draft-answer-file /tmp/draft.md --require-citation-per-paragraph \
  --formats both --output-dir /tmp/corpus_demo_check

# تنظيف
rm -rf /tmp/corpus_demo_citation /tmp/corpus_demo_check /tmp/draft.md
```

## البحث المباشر

```bash
# بحث نصي
python3 scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 5

# بحث JSON
python3 scripts/search_primary_arabic_export.py "مجلس الإدارة" --limit 5 --json

# بحث مع مرشح مسار
python3 scripts/search_primary_arabic_export.py "التصفية" --track companies_law --limit 5
```

## ملاحظات

- جميع المخرجات تذهب إلى `/tmp/` أو دليل يحدده المستخدم
- لا تُلتزم أي مخرجات مولدة في المستودع
- لا حاجة لاتصال بالشبكة
- لا حاجة لنماذج لغوية (LLM)