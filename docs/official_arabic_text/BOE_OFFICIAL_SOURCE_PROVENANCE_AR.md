# مصدرية النص العربي الرسمي — هيئة الخبراء بمجلس الوزراء
# Official Arabic Source Provenance — Bureau of Experts at the Council of Ministers

> **هذه وثيقة تصحيح مصدرية ووضع، وليست تحققًا آليًا مادةً بمادة ولا استشارة قانونية.**
> لم يُغيَّر أي نص قانوني، ولم تُعَد كتابة أي مادة، ولم تُرقَّ أي مادة، ولم يُستخدم الـOCR
> لتصحيح النص. العربية هي اللغة الحاكمة.
>
> This is a **source-provenance / status correction document — not an article-by-article
> automated verification, and not legal advice.** No legal text was changed, no article was
> rewritten, no article was promoted, and OCR was not used to correct text. Arabic is governing.

## 1. الخلاصة / Summary

قدَّم المالك للمستودع مصدرين رسميين من **هيئة الخبراء بمجلس الوزراء**:

1. **النص الكامل** لنظام الشركات باللغة العربية (المُدخَل والمقسَّم إلى 281 مادة).
2. **حزمة الـPDF الممسوحة** الرسمية (`inputs/official_arabic_verification/nizam_alsharikat_1443h_parts/`).

يُوثَّق هذان المصدران معًا بوصفهما **حزمة المصدر الرسمية الحاكمة** لسير عمل المشروع.
تبقى مخرجات الـOCR **أدلة داعمة فقط**، وليست بوابة الثقة المصدرية.

The owner provided the repository with two official sources from the **Bureau of Experts at the
Council of Ministers**: the **full Arabic text** of the Companies Law (ingested and segmented into
281 articles) and the official **scanned PDF packet**. Together they are documented as the
**controlling official source packet** for the workflow. OCR artifacts remain **supporting
evidence only**, not the source-confidence gate.

## 2. الوضع المُصحَّح / Corrected posture

| الحقل / field | القيمة / value |
|---|---|
| `source_authority` | Bureau of Experts at the Council of Ministers |
| `source_authority_ar` | هيئة الخبراء بمجلس الوزراء |
| `text_source_status` | `owner_provided_from_official_boe_source` |
| `pdf_source_status` | `owner_provided_from_official_boe_source` |
| `controlling_source_packet` | `owner_provided_boe_text_plus_pdf_packet` |
| `ocr_role` | `supporting_artifact_only_not_controlling_gate` |
| `direct_automated_capture_status` | `blocked_or_unsuitable` |
| `article_count` | `281` |
| `candidate_text_changed` | `false` |
| `no_legal_text_changed` | `true` |
| `no_article_promoted_by_ocr` | `true` |

## 3. فصل محورين / Two separated axes

نفصل **ثقة مصدرية النص** عن **التحقق الآلي مادةً بمادة**:

- **محور المصدرية / provenance axis:** `official_boe_owner_provided` — النص وحزمة الـPDF مقدَّمان
  من مصدر هيئة الخبراء الرسمي.
- **محور التحقق / verification axis:** `article_by_article_automated_verification_not_yet_performed`
  — لم يُجرِ المستودع تحققًا آليًا مباشرًا مادةً بمادة مقابل صفحات هيئة الخبراء الحية (HTML)؛
  وكان الالتقاط الآلي المباشر **متعذِّرًا أو غير ملائم**.

لذلك تبقى قيم محور الإدخال/التحقق كما هي دون تغيير، وهي تصف **محور التحقق الآلي فقط**، ولا
يجوز قراءتها على أنها تشكيك في مصدرية النص:

- `official_arabic_text_status = user_provided_source_ingested`
- `verification_status = ingested_unverified`
- `article_by_article_verified = false`
- `articles_verified = 0`

We separate **source-provenance confidence** from **article-by-article automated verification**.
The ingestion/verification-axis enum fields are retained unchanged and describe the *automated
verification axis only* — they must not be read as doubting the source provenance. The text is
official-source (Bureau of Experts) owner-provided; direct automated BOE capture was blocked or
unsuitable, and no direct automated article-by-article verification against live BOE HTML has
been performed.

## 4. دور الـOCR وقائمة المراجعة / Role of OCR and the review queue

- الـOCR على حزمة الـPDF الممسوحة **مفقودٌ الدقة (lossy)** ويُستخدم **كدليل داعم فقط**؛ ليس مرجعًا
  ولا بوابة ثقة.
- قائمة المراجعة اليدوية (`reports/official_arabic_verification/manual_review_queue.json`) تبقى
  **حاضرة كأداة فرز داعمة**، لكنها **ليست** بوابة الثقة المصدرية الحاكمة.
- سُحِبت **مراجعة دفعات OCR** (P1/P2) بوصفها بوابة تحكّم (انظر PR #46 المُغلق باعتباره مُتجاوَزًا).

OCR of the scanned PDF is **lossy** and is used as **supporting evidence only** — not a reference
and not a trust gate. The manual-review queue remains present as a supporting triage artifact but
is **not** the controlling source-confidence gate. OCR-batch review (P1/P2) is retired as a
controlling gate (see closed, superseded PR #46).

## 5. ما لم يتغيَّر / What did NOT change

- لم يتغيَّر أي `official_text_ar`؛ النص المرشح يبقى 281 مادة (بصمة SHA-256 إجمالية ثابتة يتحقق
  منها المُدقِّق).
- لم تُوسم أي مادة `verified_by_ocr` ولا `verified_against_official_gazette`.
- لم تُعدَّل طبقات LLM العربية/الإنجليزية/الصينية، ولا المرجع الإنجليزي، ولا `data/articles/`
  القائمة، ولا المخططات (schemas).

No `official_text_ar` changed (candidate stays at 281 records; a stable aggregate SHA-256 is
re-checked by the validator). No article marked `verified_by_ocr` or
`verified_against_official_gazette`. No Arabic/English/Chinese LLM layer, English reference,
existing `data/articles/`, or schema modified.

## 6. السجل التشغيلي / Operational records

- تقرير التصحيح / correction report:
  [`reports/official_arabic_verification/boe_official_source_provenance_correction.json`](../../reports/official_arabic_verification/boe_official_source_provenance_correction.json)
- بيان الإدخال / ingestion manifest:
  [`data/official_arabic/ingestion_status.json`](../../data/official_arabic/ingestion_status.json)
  (كتلة `boe_source_provenance`).
- بيانات المصدرية / provenance metadata:
  [`data/metadata/source_provenance.json`](../../data/metadata/source_provenance.json)
  (كتلة `official_arabic_foundation.boe_source_provenance`).

**العربية هي اللغة الحاكمة. هذه ليست استشارة قانونية.**
Arabic is governing. This is not legal advice.
