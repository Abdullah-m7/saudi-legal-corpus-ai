#!/usr/bin/env bash
# Reproduce every number in the manuscript, from the deposited data.
#
# Order matters only in one place: make_numbers.py reads the JSON results the
# analysis scripts write, so it runs last. Everything before it is independent
# and reads only the corpora.
#
# Runtime on one core: about a minute and a half, measured, most of it in the
# scripts that scan the full judgment corpus.
set -euo pipefail
cd "$(dirname "$0")"

ANALYSIS=../arabic_paper

echo "== corpus and citations"
python3 "$ANALYSIS/corpus_composition.py"       # what the published record is
python3 "$ANALYSIS/applied_law_v2.py"           # citations matched to instruments
python3 "$ANALYSIS/applied_articles.py"         # citations matched to articles

echo "== the four results"
python3 "$ANALYSIS/restricted_denominator.py"   # coverage under four denominators
python3 "$ANALYSIS/cite_by_voice.py"            # recital, reasoning, operative
python3 "$ANALYSIS/churn_vs_litigation.py"      # amendment against citation

echo "== robustness"
python3 "$ANALYSIS/dedup_robustness.py"         # shares over distinct texts only
python3 "$ANALYSIS/unparsed_by_year.py"         # is the parse loss time-skewed?

echo "== manuscript"
python3 make_numbers.py                         # numbers.tex, 93 macros
python3 check_numbers.py                        # refuse any hand-typed number
python3 ../check_fresh.py --stamp               # results are current again
python3 ../check_docs.py                        # and refuse a stale note
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
echo "built main.pdf"
