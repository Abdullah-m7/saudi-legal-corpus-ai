# دفعة المعالجة الصينية P0-003
# Chinese remediation batch P0-003

> **ترجمة صينية داخلية فقط، وليست رسمية ولا ملزِمة ولا حاكمة، وليست استشارة قانونية.**

## المرحلة والدفعة / Stage & batch

- **المرحلة / Stage:** `CHINESE_REMEDIATION_BATCH_P0_003`.
- **الدفعة / Batch:** **P0-003** — الأولوية **P0**، المسار `P0_no_isolable_text`.

## النطاق والمواد / Scope & articles

- **المواد المعالجة (20):** 111، 112، 114، 116، 118، 119، 120، 121، 122، 123، 124، 125، 126، 127، 128، 129، 130، 131، 134، 135.
- **الباب:** الرابع فقط (repo book4) / Bab 4 only.

## الأساس المصدري / Source basis

- **النص العربي الرسمي الحاكم** هو الأساس (`translation_basis = official_arabic_governing_text`).
- **الإنجليزية إرشاد ثانوي فقط** (`english_guidance_role = secondary_guidance_only`).
- الحالة قبل المعالجة: `excluded_no_isolable_article_text`؛ الإجراء: `create_new_internal_chinese_translation_from_arabic`.

## التسلسل القانوني / Legal hierarchy

- **العربية هي النص الحاكم.** الإنجليزية إرشاد ثانوي فقط. الصينية مرجع داخلي فقط، وليست رسمية ولا ملزِمة ولا حاكمة. ليست استشارة قانونية.

## منهجية المعالجة / Remediation methodology

أُنشئت لكل مادة ترجمة صينية داخلية جديدة من **النص العربي الرسمي الحاكم** مع الاستئناس بالإنجليزية كإرشاد ثانوي، مع الحفاظ على المعنى القانوني السعودي وأدوار الجهات والسلطات والالتزامات والحقوق والشروط والاستثناءات والمدد ومفاهيم التصويت/النصاب/رأس المال/الأسهم والآثار الإجرائية. تُخزَّن بصمات SHA-256 للنص الصيني والنص العربي المصدر والنص الإنجليزي الإرشادي.

## المخرجات المنشأة / Created artifacts

- `data/chinese_remediation_batches/p0_003/companies_law_m132_1443_zh_internal_remediation_p0_003.json`
- `reports/chinese_translation_review/CHINESE_REMEDIATION_BATCH_P0_003_AR.md`
- `scripts/validate_chinese_remediation_batch_p0_003.py`
- `tests/test_chinese_remediation_batch_p0_003.py`

## جدول المواد / Article table

| المادة | العنوان | hash العربي | hash الإنجليزي | hash الصيني | حالة الجودة |
|---|---|---|---|---|---|
| 111 | قيود تداول الأسهم | `5bbcad4bae12…` | `1813b649ce09…` | `a84531015b04…` | `pending_future_qa` |
| 112 | سجل المساهمين | `dd26b2fbe89f…` | `dca6a5908977…` | `b66e4006add3…` | `pending_future_qa` |
| 114 | شراء الأسهم وارتهانها ورهنها | `ba95c5c00e02…` | `67b13520e78f…` | `72c1c1cbe0d4…` | `pending_future_qa` |
| 116 | المطالبة بدفع ما يزيد على ما التزم به المساهم | `e85da3b4673c…` | `21edf8df5b4e…` | `797f6ad58863…` | `pending_future_qa` |
| 118 | تحويل أدوات الدين والصكوك التمويلية | `bbc6663a44cc…` | `1483c05474a8…` | `b8682a0571cd…` | `pending_future_qa` |
| 119 | التعويض عن الضرر | `218b198d0d65…` | `7f55bb30a49f…` | `7aad98eb2910…` | `pending_future_qa` |
| 120 | سريان قرارات جمعيات المساهمين | `ff6ef9112508…` | `f41497716207…` | `b8beac734a8d…` | `pending_future_qa` |
| 121 | القوائم المالية وتقرير عن نشاط الشركة | `696f8ef762f0…` | `3ff6f9a5bc2d…` | `339ba1337a81…` | `pending_future_qa` |
| 122 | تزويد المساهمين بالقوائم المالية وإيداعها | `93768a56e6c9…` | `4af8df92d67b…` | `b9d27b4c1459…` | `pending_future_qa` |
| 123 | تكوين الاحتياطيات | `290bb6cfe3d3…` | `dc3518528ec3…` | `14575694d5ba…` | `pending_future_qa` |
| 124 | استخدام الاحتياطيات | `3c300991efd6…` | `fbb3beb34258…` | `32dd0ed30d0d…` | `pending_future_qa` |
| 125 | توزيع الأرباح على المساهمين | `b51eb9a225ec…` | `54abbe57daf8…` | `60040ff3369d…` | `pending_future_qa` |
| 126 | طرق زيادة رأس المال | `b0395b6be6f0…` | `728675bab7ce…` | `e786c653feb8…` | `pending_future_qa` |
| 127 | زيادة رأس المال المصدر أو المصرح به | `ba0928fda7ff…` | `975a1f40dc9c…` | `5488f15b60cc…` | `pending_future_qa` |
| 128 | أولوية الاكتتاب بالأسهم الجديدة | `3aa525d73fe5…` | `a154ea33fbe8…` | `a473d3da91ac…` | `pending_future_qa` |
| 129 | وقف العمل بحق الأولوية | `ea0d77c7711a…` | `4bad88b6f9f5…` | `f6d3d62a4403…` | `pending_future_qa` |
| 130 | بيع حق الأولوية أو التنازل عنه | `85fdcd88315b…` | `06f1b25d79d0…` | `f216e2a9b8c1…` | `pending_future_qa` |
| 131 | توزيع الأسهم الجديدة | `b404f17f7af9…` | `d71a9cdfc849…` | `31b9fa22aa6c…` | `pending_future_qa` |
| 134 | إصدار قرار تخفيض رأس المال | `97512a4a7aeb…` | `9a4ecca4cc52…` | `73e4cac1473c…` | `pending_future_qa` |
| 135 | إجراءات تخفيض رأس المال | `5b0b4f10bb1d…` | `216ab4ab9a63…` | `dad59f3dc950…` | `pending_future_qa` |

## ملخص التحقق / Validation summary

- `make chinese-remediation-batch-p0-003-validate` — يتحقق من النطاق (20 مادة، الباب 4)، وتطابق البصمات، والوضعية الداخلية/غير الرسمية/غير المُلزِمة/غير الحاكمة، وبقاء الطبقات المحمية دون تغيير.
- `qa_status = pending_future_qa` لكل مادة (مراجعة الجودة في مرحلة لاحقة منفصلة).

## تأكيد الطبقات المحمية / Protected layers confirmation

لم تُمَس: الدفعات P0-001 (وP0-001 QA وP0-001 minor fixes) وP0-002 (وP0-002 QA)، والمرشح الصيني الداخلي (189)، وملفات الصيني القديمة (5 ملفات/23 سجلًا)، والعربي الكامل (281)، والإنجليزي الكامل (281)، والمرجع الإنجليزي (281)، والمصدر العربي الرسمي (281، `ingested_unverified`)، ومصادر الصيني المستخرجة (14)، وطابور مراجعة الـ OCR (281).

## القرار النهائي / Final decision

- **الحالة النهائية / Final status:** `REMEDIATION_DRAFT_CREATED_PENDING_FUTURE_QA`.
- **المراجعة القانونية البشرية:** ما زالت معلّقة (`pending_human_legal_review`).
- **لا توجد طبقة 281 صينية كاملة، ولا محاذاة ثلاثية، ولم تبدأ الدفعة P0-004.**

**العربية هي اللغة الحاكمة. الصينية داخلية غير رسمية وغير مُلزِمة وغير حاكمة. الإنجليزية إرشادية. ليست استشارة قانونية.**
Arabic is governing. Chinese is internal, non-official, non-binding, non-governing. English is guidance only. Not legal advice.
