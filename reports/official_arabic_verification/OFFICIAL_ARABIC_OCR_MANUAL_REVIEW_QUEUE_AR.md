# قائمة المراجعة اليدوية لمخرجات OCR — النص العربي الرسمي المرشح
# Official Arabic OCR — Manual Review Queue

> **هذه قائمة مراجعة يدوية، وليست تحققًا ولا استشارة قانونية.** لم يُغيَّر أي نص مرشح، ولم تُرقَّ أي مادة. النص المرشح يبقى `ingested_unverified` و`article_by_article_verified` يبقى `false`. المصدر الرسمي مُستخرَج بالـOCR (ذو ضجيج) ولا يُعامَل كنص حرفي.
>
> This is a **manual-review queue, not verification and not legal advice.** No candidate text was changed; no article was marked verified. This PR promotes no article.

## الحالة / Status
- النص المرشح: **`ingested_unverified`** (281 مادة، دون تغيير). / candidate unchanged.
- `article_by_article_verified` = **false** · `articles_verified` = **0** · لا مادة بحالة `verified_against_official_gazette`.

## العدد حسب فئة المراجعة / Counts by review_bucket
- `exact_match_no_action`: **3**
- `normalized_or_punctuation_review`: **8**
- `likely_ocr_noise_high_similarity`: **67**
- `likely_ocr_noise_medium_similarity`: **109**
- `possible_substantive_difference_manual_review`: **41**
- `low_similarity_manual_review`: **52**
- `missing_or_segmentation_issue`: **0**
- `resolved_segmentation_ocr_miss`: **1**

## العدد حسب الأولوية / Counts by review_priority
- **P0**: 0
- **P1**: 52
- **P2**: 41
- **P3**: 109
- **P4**: 67
- **P5**: 8
- **P6**: 4

## مواد P0 غير المُحلّة / Unresolved P0 articles
- عدد P0 غير المُحلّة / unresolved P0 count: **0**
- (لا يوجد / none)

## عناصر P0 المُحلّة / P0 resolved items
- المادة 3 / Article 3 → **resolved_segmentation_ocr_miss** — Article 3 is present on packet page 6; original P0 was caused by OCR heading ordinal corruption.

## مواد P1 (تشابه منخفض) / P1 articles (low similarity)
- 1, 12, 19, 22, 23, 55, 60, 61, 71, 76, 88, 91, 92, 93, 97, 105, 110, 113, 117, 122, 123, 126, 127, 138, 140, 141, 146, 147, 149, 150, 158, 166, 177, 178, 181, 183, 187, 188, 196, 206, 211, 212, 218, 221, 228, 248, 260, 261, 262, 264, 273, 277

## سير العمل الموصى به / Recommended manual workflow
1. راجع **P0** (المفقود/التقطيع) أولًا. / Review P0 missing/segmentation first.
2. راجع **P1** (التشابه المنخفض). / Review P1 low similarity.
3. راجع **P2** (اختلاف جوهري محتمل). / Review P2 possible substantive differences.
4. فحص عيّني لـ **P3/P4** (ضجيج OCR). / Spot-check P3/P4 OCR noise.
5. لاحقًا فقط: أنشئ PR منفصلًا للترقية/التصحيح. / Only later: a separate promotion/correction PR.

**هذا الـPR لا يرقّي أي مادة. العربية هي اللغة الحاكمة. ليست استشارة قانونية.** This PR promotes no article. Arabic is governing. Not legal advice.
