# Corpus Resource Paper

Academic resource paper documenting this repository's corpus, targeted at
LREC / NLLP / Language Resources and Evaluation.

| File | Purpose |
|---|---|
| `saudi_legal_corpus_resource_paper.md` | The paper draft (English). |
| `ARABIC_SUMMARY_AR.md` | Arabic companion summary + pre-submission checklist. |
| `generate_corpus_paper_stats.py` | Read-only script that computes every statistic cited in the paper. |
| `corpus_paper_stats.json` | Generated statistics snapshot (regenerate with the script). |

Reproduce all paper statistics from the repository root:

```
python3 docs/research/corpus_paper/generate_corpus_paper_stats.py
```

The script is read-only over `data/` and deterministic (no network, no
wall-clock time), consistent with the repository's validator conventions.
