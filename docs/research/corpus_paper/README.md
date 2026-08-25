# Corpus Resource Paper

Academic resource paper documenting this repository's corpus, targeted at
LREC / NLLP / Language Resources and Evaluation.

**Submitted to *Language Resources and Evaluation* (Springer) via Snapp.
Status as of 25 August 2026: `Under Consideration` — submission checks
complete, editor not yet assigned.** Springer Nature reports progress on the
Research Square tracking dashboard (<https://www.researchsquare.com/>), which
is where these status lines come from; Snapp itself issues no manuscript
number visible to the author at this stage.

| File | Purpose |
|---|---|
| `saudi_legal_corpus_resource_paper.md` | The paper draft (English). |
| `ARABIC_SUMMARY_AR.md` | Arabic companion summary + pre-submission checklist. |
| `generate_corpus_paper_stats.py` | Read-only script that computes every corpus statistic cited in the paper. |
| `corpus_paper_stats.json` | Generated statistics snapshot (regenerate with the script). |
| `bm25_baseline.py` | Okapi BM25 baseline over the unified index, evaluated on the 519 gold queries (overall + per category). |
| `bm25_baseline_results.json` | Generated BM25 results snapshot (regenerate with the script). |
| `domain_coverage.py` | Author-assigned domain grouping (explicit keyword rules over identifiers) behind the journal version's coverage table. |
| `domain_coverage.json` | Generated domain-coverage snapshot (regenerate with the script). |
| `latex/` | **Conference version** — ACL/NLLP-style two-column LaTeX source, Figure 1 and its generator, and compiled `main.pdf`. |
| `journal/` | **Journal version** — expanded single-column Springer manuscript targeted at *Language Resources and Evaluation*, with Declarations and a coverage-by-domain section. |

**Two submission targets, two manuscripts.** `journal/` is the current
primary target (*Language Resources and Evaluation*); `latex/` holds the
shorter conference version. The Markdown file mirrors the conference version
for in-repository reading. A manuscript may be under review at only one of
them at a time.

Reproduce all paper statistics from the repository root:

```
python3 docs/research/corpus_paper/generate_corpus_paper_stats.py
```

The script is read-only over `data/` and deterministic (no network, no
wall-clock time), consistent with the repository's validator conventions.
