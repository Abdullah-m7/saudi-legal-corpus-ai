# Corpus Registry

The canonical corpus registry (`corpus_registry.json`) is a lightweight,
machine-readable index that summarizes and links all completed corpus tracks
in the repository.

## Purpose

- Improve project navigability and future automation
- Expose counts, paths, statuses, languages, boundaries, and validation targets
- Support future export, search, RAG, translation planning, and corpus navigation
- Freeze the current state of completed tracks

## What this is NOT

- Not a new legal corpus layer
- Not an export system, RAG demo, or search index
- Not a translation or legal analysis tool
- Not an official government publication

## Count Semantics

The registry uses explicit count fields with a `count_policy` object to avoid ambiguity.

**Counting method:** raw layer records, not deduplicated legal article units.

**Count fields:**

| Field | Value | Formula |
|-------|-------|---------|
| `total_primary_arabic_governing_records` | 450 | CL Arabic(281) + Gen IR articles(95) + Gen IR forms(4) + LJS articles(69) + LJS appendix(1) |
| `total_reference_records` | 281 | CL English(281) |
| `total_internal_reference_records` | 281 | CL Chinese remediation(281) |
| `total_implementing_regulations_records` | 169 | Gen articles(95) + Gen forms(4) + LJS articles(69) + LJS appendix(1) |
| `total_registry_counted_records` | 1012 | Primary Arabic(450) + Reference(281) + Internal ref(281) |

**Key policy decisions:**
- Closure audit aggregate (169) is NOT added separately — it duplicates underlying IR records
- Chinese remediation (281) IS counted as internal reference records
- Forms and appendices ARE counted as records
- English reference records ARE counted

## Tracks

1. **companies_law** — Saudi Companies Law (M/132, 1443H), 281 articles
   - Arabic governing layer (281 records)
   - English reference/guidance layer (281 records)
   - Chinese internal remediation complete (281 articles, P0–P3)

2. **implementing_regulations_general** — General implementing regulations
   - 95 articles + 4 forms
   - Arabic Legal LLM-ready layer

3. **implementing_regulations_listed_joint_stock** — Listed joint-stock regulation
   - 69 articles + 1 appendix
   - Specialized (NOT general)

4. **implementing_regulations_arabic_program_closure** — Closure audit
   - 164 article records + 5 non-article records = 169 total

## Legal Boundaries

- Arabic official source governs
- Not official translation
- Not legal advice
- No trilingual alignment
- No public release
- English = reference/guidance only
- Chinese = internal reference only

## Validate

```bash
make corpus-registry-validate
```

## Generator

```bash
python3 scripts/gen_corpus_registry.py
```

The generator is idempotent — re-running produces identical output.