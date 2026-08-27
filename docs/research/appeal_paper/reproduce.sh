#!/usr/bin/env bash
# Reproduce every number in paper 9, from the deposited data.
#
# The appellate layer sits inside the same records as the judgments, so there
# is nothing extra to collect: these scripts read the corpus that paper 8
# already deposits.
set -euo pipefail
cd "$(dirname "$0")"
A=../arabic_paper

echo "== the corpus, and what became of each judgment"
python3 "$A/corpus_composition.py"
python3 "$A/appellate_outcome.py"
python3 "$A/appeal_reasons.py"

echo "== the two levels compared, and the selection that threatens it"
python3 "$A/appeal_vs_first.py"
python3 "$A/appeal_selection.py"

echo "== what predicts disturbance"
python3 "$A/reversal_model.py"                      # the whole span
python3 "$A/reversal_model.py" --from 1439 --to 1444  # the mature window

echo "== manuscript"
python3 make_numbers.py
python3 check_numbers.py
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
echo "built main.pdf"
