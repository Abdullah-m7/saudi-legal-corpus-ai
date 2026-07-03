# `data/official_arabic/` — official Arabic statutory text (canonical target)

This folder is the **target home for the OFFICIAL Arabic statutory text** of the Saudi
Companies Law (all **281 articles**), which is intended to become the **canonical legal
source** of this repository. **It is currently empty of article records** — no official
Arabic statutory text has been ingested yet.

## Current status

- `ingestion_status.json` — the authoritative foundation-provenance record. It states,
  honestly, that:
  - `official_arabic_text_status = not_ingested`
  - `article_by_article_verified = false`
  - `verification_status = pending_official_source`
  - the current Arabic content elsewhere in the repo is
    `internally_reviewed_reference_summary_not_official`.

## What goes here (later, only after an official source is provided)

Per-article JSON records validating against
[`schemas/official_arabic_article.schema.json`](../../schemas/official_arabic_article.schema.json),
each carrying the **verbatim** `official_text_ar`, its `text_hash_sha256`, the full source
provenance, and a `verification_status`. A record may only be marked
`verified_against_official_gazette` after a real article-by-article check.

## How to start

1. Provide an official source packet — see
   [`docs/official_arabic_text/SOURCE_PACKET_REQUIREMENTS_AR.md`](../../docs/official_arabic_text/SOURCE_PACKET_REQUIREMENTS_AR.md).
2. Follow the verification plan —
   [`docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md`](../../docs/official_arabic_text/OFFICIAL_ARABIC_VERIFICATION_PLAN_AR.md).

**Do not** paste unofficial blog/third-party copies here as if canonical, and **do not**
mark anything verified unless it was actually verified against the official source.

Arabic remains the governing legal language throughout. This material is not legal advice.
