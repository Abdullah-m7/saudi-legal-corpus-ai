# Labor Law English Reference Layer - Batch 002 Scaffold

**Scope:** Second scaffold batch for 20 high-confidence clean Arabic Labor Law articles (no overlap with Batch 001).

**Purpose:** Extend the English reference scaffold. All records OFFICIAL_ENGLISH_PENDING pending official English source packet.

**Selection Criteria:**
- Clean/reconciled from official Arabic source
- No unresolved_issue_flag
- Not deleted/abolished
- Not amendment-popup/manual/pending/renumbered/mukarrar
- No overlap with Batch 001 article_keys
- Not dependent on unmerged Hermes PR #131
- Early clean articles preferred

**Official English Source Status:** SOURCE_PACKET_REQUIRED (no official English Labor Law guidance source present).

All records have:
- english_reference_status = OFFICIAL_ENGLISH_PENDING
- english_text = ""
- source_packet_required = true

**Records:** 20
**No overlap with Batch 001:** Confirmed

**Excluded articles (dependent on unmerged Hermes PR #131 or blocked):**
- labor_law_art_003
- labor_law_art_005
- labor_law_art_007
- labor_law_art_027 (DO_NOT_INGEST_YET / BLOCKED_POPUP_BASE_STRUCTURE)
- labor_law_art_030

**Validation:** Run the existing checker from Batch 001.

No legal advice. No official translation claim. Reference layer only.