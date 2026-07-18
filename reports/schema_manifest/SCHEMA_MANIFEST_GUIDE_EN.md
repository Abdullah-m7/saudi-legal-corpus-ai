# Corpus Schema Manifest — Guide for External Integrators

This is the **English-language companion guide** to
[`data/schema_manifest/corpus_schema_manifest.json`](../../data/schema_manifest/corpus_schema_manifest.json),
the authoritative, machine-readable manifest of every JSON Schema used across
this corpus. It exists because most of this corpus's documentation
(`STATUS.md`, per-track `notes`, methodology write-ups) is Arabic-facing and
assumes familiarity with the repository's own history; this guide instead
targets an **external developer or integrator** — for example, someone
building a RAG (retrieval-augmented generation) application on top of this
corpus — who needs to understand the data model without reading 123+
individual track files and their generator scripts.

This guide, and the manifest it documents, are **read-only, descriptive**
artifacts. Nothing here alters any of the corpus's 123 tracks, the registry,
or any other corpus-wide derived layer. **Not legal advice.** Arabic is the
governing language for every law/regulation text in this corpus; this guide
and the manifest are themselves in English only because they describe the
*data model*, not the law.

---

## 1. Directory layout

Every one of this corpus's 123 tracks (a "track" = one law, one implementing
regulation, one set of procedural rules, etc.) follows the same three-stage
layout, plus six read-only, corpus-wide layers built on top of all tracks
together:

```
sources/<track>/<component>/
    official_source/*.json          # stage 1: source-of-truth document
    verified/*.jsonl                 # stage 2: flattened, verified text
    (verified/*_verified_summary.json)
    moj_cross_check/ (a few tracks)  # extra cross-check audit trail

data/<track>_arabic_legal_llm/*.json # stage 3: LLM-ready retrieval layer
                                      # (naming varies: some tracks use
                                      #  official_arabic_legal_llm/,
                                      #  chinese_legal_llm/, etc. — see
                                      #  gen_corpus_unified_llm_index.py's
                                      #  LAYERS list for the exhaustive map)

data/corpus_unified_index/           # corpus-wide: flat index over ALL tracks
data/corpus_registry/                # corpus-wide: canonical track catalog
data/corpus_verification_tiers/      # corpus-wide: confidence classification
data/corpus_supersession_graph/      # corpus-wide: repeal/supersession edges
data/corpus_cross_reference_graph/   # corpus-wide: article "see also" edges
data/corpus_glossary/                # corpus-wide: cross-law term definitions

data/schema_manifest/                # THIS deliverable: the schema manifest
reports/schema_manifest/             # THIS deliverable: this guide
```

`<track>` here is a directory name like `civil`, `income_tax`, `patent`,
`zakat`, `traffic`. `<component>` is `law`, `regulation`,
`implementing_regulation`, `case_rules`, `annex1`, etc. — a track can have
more than one component (e.g. `arbitration` has both `law` and
`implementing_regulation`; `zakat` currently has only `law`).

### A naming gotcha you will hit immediately

The **track key used in `data/corpus_unified_index/`** (its `corpus` field)
is almost always **different** from the **`track_id` used in
`corpus_registry.json` / `corpus_verification_tiers.json` / both graph
files / `corpus_glossary.json`**:

| Layer | Example identifier for the Civil Transactions Law |
|---|---|
| `sources/` and `data/` directory name | `civil` |
| unified index `corpus` field | `civil` |
| registry `track_id` (and every other corpus-wide layer's `track_id`) | `civil_transactions_law` |

Of the corpus's 123 registry `track_id`s, **121 do not literally equal** the
unified-index `corpus` key for the same track — the registry `track_id`
almost always adds a component suffix (`_law`, `_regulation`,
`_implementing_regulation`, `_case_rules`, ...), and one bare `corpus` key
can map to **two** `track_id`s (e.g. `arbitration` → `arbitration_law` **and**
`arbitration_implementing_regulation`, disambiguated by `law_component`).

**The reliable way to go from a registry `track_id` to its unified-index
`corpus` key** is to read the `_arabic_legal_llm` directory name out of that
track's own `data_paths` in the registry — not to guess a string
transformation. Section 4's quick-start does exactly this.

---

## 2. How the layers relate to each other

```
official_source.json  →  verified/*.jsonl  →  <track>_arabic_legal_llm/*.json
        │                                              │
        │ (read by 5 corpus-wide generators)           │ (read by gen_corpus_unified_llm_index.py)
        ▼                                              ▼
 corpus_registry.json ◄────────────────────── corpus_unified_llm_index.jsonl
        │
        ├──► corpus_verification_tiers.json      (derives a tier from registry.tracks[].official_text_status)
        ├──► corpus_supersession_graph.json       (hand-curated edges, validated against registry track_ids)
        ├──► corpus_cross_reference_graph.json    (regex-extracted from the unified index's text)
        └──► corpus_glossary.json                 (regex-extracted from the unified index's text)

 reports/coverage_gap_map/coverage_gap_map.json    (a standalone research artifact — hand-authored,
                                                     no dedicated generator script, lists laws NOT
                                                     yet in the corpus plus laws deliberately excluded)
```

- **`official_source.json`** is the closest thing to raw ingestion: the full
  article text, chapter/section structure, and a long verification-methodology
  narrative, produced by one dedicated per-track generator script. This is
  **the least standardized layer in the corpus** — see §3 below.
- **`verified/*.jsonl`** flattens `official_source.json` into one JSON object
  per article, adding explicit `is_amended`/`is_repealed`/`is_added` booleans
  and a `verification_status` string, but no retrieval metadata (no keywords,
  no search queries, no content hash).
- **`<track>_arabic_legal_llm/*.json`** is the **LLM/RAG-ready layer** — an
  envelope plus a `records` array, each record carrying the article text,
  a sha256 content hash, generated keyword lists, generated search-query
  strings, and a `source_trust` sub-object. **This is the layer most directly
  useful to a RAG integrator working with one specific law.**
- **`corpus_unified_llm_index.jsonl`** flattens *every* track's
  `_arabic_legal_llm` layer into one JSONL file with one common field set —
  **this is the single flattest, most corpus-spanning entry point** if you
  want to search or filter across the whole corpus at once rather than one
  law at a time.
- **`corpus_registry.json`** is the canonical catalog: one entry per track,
  pointing at all of that track's files, its record counts, and its
  boundaries/disclaimers. Nearly every other corpus-wide layer reads *this*
  file as its own upstream source (not the raw track files directly).
- **`corpus_verification_tiers.json`**, **`corpus_supersession_graph.json`**,
  **`corpus_cross_reference_graph.json`**, and **`corpus_glossary.json`** are
  four independent, read-only **derived** layers built on top of the registry
  (and, for the two graph layers, on top of the unified index's article
  text). None of them modify the registry or any track file; each is
  produced and validated by its own dedicated generator/validator script pair
  and documents its own extraction caveats.
- **`reports/coverage_gap_map/coverage_gap_map.json`** is different in kind
  from the other five: it has no dedicated generator script (it is a
  hand-authored research artifact) and it describes laws **not** in the
  corpus (or deliberately excluded), rather than describing the corpus's own
  content.

---

## 3. What varies, and why (field provenance summary)

The full, field-by-field breakdown lives in the manifest's
`field_provenance_notes` key. The short version:

- **`official_source_schema` is the least standardized layer.** A broad
  structural sweep run by the manifest's own generator
  (`data/schema_manifest/corpus_schema_manifest.json`'s
  `corpus_wide_coverage_check` key) found that only a **minority** of the
  corpus's 117+ `official_source.json` files match either of the two
  deeply-documented conventions (**STANDARD**, confirmed on `income_tax_law`,
  `patent_law`, `zakat_law`, `traffic_law`, `social_insurance_law`,
  `basic_law_of_governance`; **LEGACY**, confirmed on
  `civil_transactions_law` only, the corpus's earliest track). A third,
  deliberately permissive **MINIMAL** fallback (just `article_count` +
  `articles`) is included in the schema so it still *accepts* — without
  claiming to deeply model — the many further real conventions this pass
  did not read in full depth (e.g. `aawan_regulation` uses `stats`/
  `provenance` instead of `status_counts`/`verification_methodology_note`;
  `labor_law` uses a civil-like-but-not-identical shape; `anti_bribery_law`
  omits `chapter_structure`/`preamble_ar` entirely).
- **`verified_record_schema` and `llm_ready_layer_schema` generalize much
  better** — the same coverage sweep found roughly 80% of the corpus's real
  `verified/*.jsonl` and `_arabic_legal_llm/*.json` files match one of the
  two modeled conventions, because these are later normalization stages that
  converge more even though they were written by many separate per-track
  generator scripts.
- **Track-specific fields worth knowing about**, with their pioneering track:
  - `decree_transitional_provisions_ar` — **social_insurance_law** only.
  - `provenance` (structured source-access metadata) — **basic_law_of_governance** only.
  - `original_<HHHHh>_text` (pre-amendment article wording; the field NAME
    itself encodes the track's founding Hijri year) —
    **basic_law_of_governance** (`original_1412h_text`),
    **income_tax_law**/**patent_law** (`original_1425h_text`),
    **traffic_law** (`original_1428h_text`), **zakat_law**
    (`original_1445h_text`); absent entirely from **social_insurance_law**
    and **civil_transactions_law**.
  - Per-article `verification_tier` — pioneered by **traffic_law** (67 of 86
    articles `PRIMARY_INDEPENDENTLY_CONFIRMED` vs. 19 of 86
    `SECONDARY_SOURCE_ONLY_BOE_KNOWN_STALE`); also on **basic_law_of_governance**
    (Article 5 only).
  - `cross_verified_against_wipo_lex` (per-article boolean) — **basic_law_of_governance** only.
  - `chapter_structure[]` item shape — **at least three incompatible
    conventions** even among the six standard-convention tracks sampled;
    treat it as display prose, not a reliable machine article-range index.
  - `corpus_registry_track_schema`'s `official_text_status` is null/absent on
    exactly the **4 earliest tracks** (`companies_law` and its two sibling
    `implementing_regulations_*` tracks, plus the `implementing_regulations_
    arabic_program_closure` audit track) — they predate the verification-
    tiering convention and are hand-assigned a tier via a separate lookup
    table inside `gen_corpus_verification_tiers.py`.
  - `boundaries.specialized_scope` — a free-text string key living inside an
    otherwise-boolean `boundaries` object, unique to
    `implementing_regulations_listed_joint_stock`.
  - Glossary terms with **more than one definition entry** (92 of 696 terms
    in the current corpus) signal a term whose legal meaning may genuinely
    differ by law — e.g. `إعادة التأهيل` ("rehabilitation") is defined
    separately, and differently, by both `environmental_law` and
    `mining_investment_law`.

---

## 4. Quick start: pull all Tier-1 verified articles mentioning a glossary term

This walks through a concrete, runnable example: **find every article, from
only the corpus's highest-confidence ("Tier 1") tracks, that mentions a
specific glossary term.** All four files below are already present in this
repository; nothing needs to be generated first.

```python
import json, re

ROOT = "."  # repo root

# 1. Load the four files this quick-start needs.
registry = json.load(open(f"{ROOT}/data/corpus_registry/corpus_registry.json", encoding="utf-8"))
tiers = json.load(open(f"{ROOT}/data/corpus_verification_tiers/corpus_verification_tiers.json", encoding="utf-8"))
glossary = json.load(open(f"{ROOT}/data/corpus_glossary/corpus_glossary.json", encoding="utf-8"))

# 2. Which registry track_ids are Tier 1 (2+ independent primary/official
#    sources agree, no reachability gap)?
tier1_track_ids = {
    t["track_id"] for t in tiers["tracks"]
    if t["tier"] == "TIER_1_PRIMARY_MULTI_SOURCE"
}

# 3. Resolve each Tier-1 track_id to its unified-index `corpus` key. Do NOT
#    guess a string transform (see the naming gotcha in section 1) — read it
#    out of the track's own data_paths instead.
track_to_corpus_key = {}
for t in registry["tracks"]:
    for p in t.get("data_paths", []):
        m = re.search(r"data/([a-z0-9_]+)_arabic_legal_llm/", p)
        if m:
            track_to_corpus_key.setdefault(t["track_id"], set()).add(m.group(1))

tier1_corpus_keys = set()
for tid in tier1_track_ids:
    tier1_corpus_keys |= track_to_corpus_key.get(tid, set())

print(f"{len(tier1_track_ids)} Tier-1 tracks -> {len(tier1_corpus_keys)} unified-index corpus keys")

# 4. Pick a glossary term and see which track(s) formally define it (optional —
#    you can also just pick any Arabic term/phrase you care about directly).
term = "أمين الإفلاس"   # "bankruptcy trustee" — defined in bankruptcy_law's own
                          # definitions article (Tier 1)

# 5. Scan the unified index (one flat JSONL file, one line per article across
#    every track) for articles whose text mentions the term AND whose
#    `corpus` key belongs to a Tier-1 track.
hits = []
with open(f"{ROOT}/data/corpus_unified_index/corpus_unified_llm_index.jsonl", encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        if rec["corpus"] in tier1_corpus_keys and term in (rec.get("text_ar") or ""):
            hits.append(rec)

print(f"Found {len(hits)} Tier-1 article(s) mentioning '{term}':")
for h in hits:
    print(f"  [{h['corpus']}] {h['retrieval_title_ar']}")
```

Running this against the corpus as committed prints:

```
89 Tier-1 tracks -> 61 unified-index corpus keys
Found 8 Tier-1 article(s) mentioning 'أمين الإفلاس':
  [bankruptcy] نظام الإفلاس - المادة الأولى:
  [bankruptcy] نظام الإفلاس - المادة الخامسة والتسعون بعد المائة:
  ... (6 more)
```

From here, a RAG pipeline would typically:

1. Use `unified_index_record_schema`'s `text_ar` field as the chunk to embed,
   and `record_id`/`article_path` as the citation you show the end user.
2. Cross-check `text_status` (or, per-track, the fuller `verification_status`
   in `verified_record_schema`) before presenting a claim as settled —
   remember some tracks have per-article `verification_tier` variation (see
   §3) even within an otherwise Tier-1 or Tier-4 track.
3. Before citing an article as *currently in force*, check
   `corpus_supersession_graph.json`'s `edges` for a `relation="superseded_by"`
   or `relation="repeals_partial"` entry naming that track — e.g.
   `copyright_law` is confirmed superseded effective 2026-08-01 but the
   successor's text is not yet ingested, and `commercial_courts_law`'s own
   evidence chapter (articles 38-57) is `is_repealed=true` because
   `evidence_law` now governs that subject matter instead.
4. Use `corpus_cross_reference_graph.json`'s `references` array to surface
   "see also" links for an article the user is reading — remembering this
   graph is an explicitly best-effort, regex-based NLP extraction, not an
   independently verified dataset like the article text itself.

---

## 5. Where to look next

- **`data/schema_manifest/corpus_schema_manifest.json`** — the full JSON
  Schema for all 9 document types described above, plus
  `field_provenance_notes` (the complete version of §3) and
  `corpus_wide_coverage_check` (the complete version of the coverage numbers
  cited in §3).
- **`scripts/gen_corpus_schema_manifest.py`** — the generator; re-run it any
  time to regenerate the manifest (it self-validates on every run and fails
  loudly if a claimed "always present" field is missing from a sampled real
  file).
- **`scripts/validate_corpus_schema_manifest.py`** — an independent
  structural validator: confirms every schema is syntactically valid JSON
  Schema (via the `jsonschema` library's `Draft202012Validator` when
  available), cross-checks a *different* sample of real files than the
  generator's own self-check, and confirms the generator is idempotent.
- **`data/corpus_registry/corpus_registry.json`** — for a plain-English (well,
  mostly Arabic-narrative) summary of every one of the 123 tracks, including
  its own `notes` field, which is often the fastest way to understand one
  specific law's provenance and caveats without reading its
  `official_source.json` in full.
