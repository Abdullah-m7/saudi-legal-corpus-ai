# Corpus Export — Primary Arabic Governing Records (v1)

## نظرة عامة

This directory contains the v1 export of primary Arabic governing records from the Saudi legal corpus.

## Scope

- **Included:** 450 Arabic governing records
  - Companies Law Arabic articles: 281
  - General implementing regulations articles: 95
  - General implementing regulations forms: 4
  - Listed joint-stock implementing regulation articles: 69
  - Listed joint-stock implementing regulation appendix: 1

- **Excluded from this export:**
  - English reference records
  - Chinese internal reference records
  - Closure audit aggregate records (duplicate underlying IR records)

## Format

- **primary_arabic_governing_records.jsonl** — JSONL, one record per line
- **export_manifest.json** — export metadata, counts, count_policy, legal boundaries

## Record fields

Each JSONL record includes:

| Field | Description |
|-------|-------------|
| `export_record_id` | Unique export identifier |
| `source_track_id` | Registry track ID |
| `source_record_id` | Original corpus record ID |
| `corpus_family` | companies_law or implementing_regulations |
| `document_type` | statutory_law or implementing_regulation |
| `record_type` | article, form, or appendix |
| `language` | ar |
| `governing_status` | arabic_governing_text |
| `title_ar` | Article/form/appendix title in Arabic |
| `article_number` / `record_number` | When available |
| `text_ar` | Official Arabic text — verbatim from source |
| `source_text_sha256` | Hash of source text |
| `source_url` | When available |
| `source_authority` | When available |
| `publication_date_hijri` | When available |
| `publication_date_gregorian` | When available |
| `source_data_path` | Path to source corpus file |
| `registry_track_id` | Registry track reference |
| `legal_boundaries` | Legal boundary flags |
| `notes` | Additional notes when necessary |

## Text preservation

`text_ar` is copied verbatim from existing canonical corpus fields. No paraphrase, no summary, no normalization that changes legal text.

## Legal boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No trilingual alignment
- No public release
- English = reference/guidance only (not exported in this stage)
- Chinese = internal reference only (not exported in this stage)
- Listed JSC specialized, NOT general

## Generation

```bash
python3 scripts/gen_corpus_export_primary_arabic.py
```

## Validation

```bash
make corpus-export-primary-arabic-validate
```

## Idempotence

The generator is deterministic. Re-running produces identical output.

```bash
python3 scripts/gen_corpus_export_primary_arabic.py
git diff --exit-code  # should be 0
```