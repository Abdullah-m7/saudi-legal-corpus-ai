# Corpus Resource Paper

Academic resource paper documenting this repository's corpus, targeted at
LREC / NLLP / Language Resources and Evaluation.

| File | Purpose |
|---|---|
| `saudi_legal_corpus_resource_paper.md` | The paper draft (English). |
| `ARABIC_SUMMARY_AR.md` | Arabic companion summary + pre-submission checklist. |
| `generate_corpus_paper_stats.py` | Read-only script that computes every corpus statistic cited in the paper. |
| `corpus_paper_stats.json` | Generated statistics snapshot (regenerate with the script). |
| `bm25_baseline.py` | Okapi BM25 baseline over the unified index, evaluated on the 519 gold queries (overall + per category). |
| `bm25_baseline_results.json` | Generated BM25 results snapshot (regenerate with the script). |
| `latex/` | LaTeX source (`main.tex`, `references.bib`), Figure 1 (`example_record.png` + its generator), and compiled `main.pdf`; venue-adaptive (ACL/NLLP style kit auto-detected, self-contained fallback otherwise). |

The LaTeX version is the canonical submission text; the Markdown mirrors it
for in-repository reading.

Reproduce all paper statistics from the repository root:

```
python3 docs/research/corpus_paper/generate_corpus_paper_stats.py
```

The script is read-only over `data/` and deterministic (no network, no
wall-clock time), consistent with the repository's validator conventions.
