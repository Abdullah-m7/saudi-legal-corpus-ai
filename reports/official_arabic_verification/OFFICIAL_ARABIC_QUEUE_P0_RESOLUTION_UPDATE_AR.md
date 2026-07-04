# تحديث قائمة المراجعة — حلّ عنصر P0 (المادة الثالثة)
# Manual-Review Queue Update — P0 Resolution (Article 3)

> **هذا تحديث حالة لقائمة المراجعة فقط، وليس تحققًا ولا استشارة قانونية.** لم يُغيَّر أي نص مرشح،
> ولم تُرقَّ أي مادة، ولم تُوسم أي مادة بأنها `verified_against_official_gazette`. النص المرشح يبقى
> `ingested_unverified` و`article_by_article_verified` يبقى `false`.
>
> This is a **queue status update only — not verification, not legal advice.** No candidate text
> was changed; no article was promoted or marked verified.

## ما تم / What changed

- تم تعليم عنصر **P0 الوحيد** (المادة الثالثة — جنسية الشركة) على أنه **محلول** بسبب خطأ تقطيع
  في الـOCR. / The single P0 item (Article 3) is marked **resolved** as an OCR segmentation miss.
- استنادًا إلى:
  [`reports/official_arabic_verification/p0_article3_segmentation_review.json`](p0_article3_segmentation_review.json)
  ([التقرير العربي](P0_ARTICLE3_SEGMENTATION_REVIEW_AR.md)).

## المادة الثالثة / Article 3

| الحقل / field | قبل / before | بعد / after |
|---|---|---|
| `review_bucket` | `missing_or_segmentation_issue` | `resolved_segmentation_ocr_miss` |
| `review_priority` | `P0` | `P6` |
| `p0_resolution_status` | — | `resolved` |
| `p0_resolution_classification` | — | `segmentation_ocr_miss` |
| `verification_action_allowed` | `false` | `false` |

- **ملاحظة الحل / resolution note:** المادة الثالثة موجودة في المصدر الرسمي الممسوح (صفحة الحزمة 6)؛
  وكان سبب P0 الأصلي تلف ترتيب العنوان في الـOCR (الثالثة → الثالئة). / Article 3 is present on
  packet page 6; the original P0 was caused by OCR heading-ordinal corruption.

## التحوّلات في العدّاد (يبقى المجموع 281) / Count shifts (total stays 281)

- **عدد P0 غير المُحلّة / unresolved P0 count:** `1` → **`0`**.
- **`resolved_segmentation_ocr_miss`:** `0` → **`1`**.
- **`missing_or_segmentation_issue`:** `1` → **`0`**.
- **`P6`:** `3` → **`4`** (3 مطابقات تامة + 1 عنصر P0 محلول). / (3 exact + 1 resolved P0).
- بقية الفئات/الأولويات دون تغيير. / all other buckets/priorities unchanged.
- إجمالي العناصر / total entries: **281** (دون تغيير / unchanged).

## الوضع بعد التحديث / Post-update state

- **عناصر P0 غير المُحلّة: لا يوجد (0).** / Unresolved P0 items: none (0).
- **عناصر P0 المُحلّة:** المادة **3** — `resolved_segmentation_ocr_miss` (موجودة في صفحة الحزمة 6).
- النص المرشح: **281 مادة، `ingested_unverified`، دون تغيير.** / candidate: 281 records,
  ingested_unverified, unchanged.

**هذا الـPR لا يرقّي ولا يتحقق ولا يصحّح ولا يغيّر أي نص قانوني. العربية هي اللغة الحاكمة. ليست استشارة قانونية.**
This PR does not promote, verify, correct, or modify any legal text. Arabic is governing. Not legal advice.
