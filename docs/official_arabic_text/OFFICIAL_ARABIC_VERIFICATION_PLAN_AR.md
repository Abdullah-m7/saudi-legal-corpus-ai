# خطة التحقق من النص العربي الرسمي — Official Arabic Verification Plan

> **الهدف / Goal:** إدخال النص العربي النظامي الرسمي لنظام الشركات (المواد 1–281) والتحقق منه
> مادةً مادةً، وترقيته ليكون **المصدر القانوني القانوني (canonical)**، دون كسر الطبقات الحالية،
> ودون ادعاء أن الملخصات الحالية نص رسمي. / Ingest and verify the official Arabic statutory
> text (Articles 1–281) article-by-article and promote it to the **canonical** legal source,
> without breaking existing layers and without pretending the current summaries are official
> text.

This plan is execution-oriented. Each phase has a concrete entry condition, action, and exit
condition. **Nothing is marked verified until Phase E succeeds against a real official source.**

## Phase A — Source packet registration / تسجيل حزمة المصدر
- **Entry:** owner provides an official source packet per
  [`SOURCE_PACKET_REQUIREMENTS_AR.md`](SOURCE_PACKET_REQUIREMENTS_AR.md).
- **Action:** record it in `data/official_arabic/ingestion_status.json`
  (`source_url_or_file_reference`, `source_document_type`, `source_authority`,
  `source_publication_reference`, gazette issue/date, royal decree number/date); set
  `official_source_required` handling and `verification_status = ingested_unverified` only
  once files are actually present.
- **Exit:** the official source file(s) exist in the repo/packet and are parseable.

## Phase B — Extraction / الاستخراج
- **Entry:** Phase A complete.
- **Action:** extract the official Arabic text from the packet (official text layer, or
  OCR-of-scan + manual correction if the source is an image). Record `extraction_method`.
- **Exit:** a raw official Arabic text blob exists, faithful to the source.

## Phase C — Article segmentation 1–281 / تقطيع المواد
- **Entry:** Phase B complete.
- **Action:** segment the raw text into **281** article records against
  [`schemas/official_arabic_article.schema.json`](../../schemas/official_arabic_article.schema.json),
  each carrying the verbatim `official_text_ar` and `article_number`.
- **Exit:** exactly 281 article records exist, each schema-valid, none invented.

## Phase D — Hash each article / بصمة كل مادة
- **Entry:** Phase C complete.
- **Action:** compute `text_hash_sha256 = sha256(official_text_ar utf-8)` for every article
  to lock the exact text and detect later drift.
- **Exit:** every official article record has a correct 64-hex `text_hash_sha256`.

## Phase E — Compare existing layers against official Arabic article IDs / المطابقة
- **Entry:** Phase D complete.
- **Action:** align, article-by-article, the existing Arabic summaries, the official English
  reference, and the Chinese layer to the official Arabic article numbers; flag mismatches
  (numbering, scope, missing/extra articles). No derived text is edited here — this is a
  comparison/report step.
- **Exit:** an alignment report exists; each article is either matched or flagged.

## Phase F — Promote official Arabic text to canonical source / الترقية
- **Entry:** Phase E complete AND a human reviewer confirms.
- **Action:** set `article_by_article_verified = true` and, per article,
  `verification_status = verified_against_official_gazette` and
  `manual_review_status = manually_reviewed`. Update NOTICE/provenance to state the official
  Arabic text is now canonical. **Only** verified articles may carry the verified status.
- **Exit:** official Arabic text is the canonical legal source; summaries are explicitly
  derived/secondary.

## Phase G — Regenerate derived layers only after verification / إعادة التوليد
- **Entry:** Phase F complete for the relevant articles.
- **Action:** regenerate/re-align the derived English/Chinese/LLM layers to the official
  Arabic article IDs. Never regenerate a derived layer as "official-aligned" before its
  official Arabic anchor is verified.
- **Exit:** all layers reference verified official Arabic article IDs.

## Guardrails / ضوابط
- No official Arabic text is invented, pasted from unofficial copies, or scraped blindly.
- No article is marked `verified_against_official_gazette` without a real check against the
  registered official source.
- Current Arabic summaries stay `internally_reviewed_reference_summary_not_official` until
  Phase F.
- Arabic remains the governing legal language. Not legal advice.
