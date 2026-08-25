#!/usr/bin/env bash
# Collect every judgment matching each of paper 3's four conflicting terms.
#
# Smallest first, so something is readable within the hour rather than at the
# end. Details are cached by judgment id, so the overlap between terms costs
# nothing and an interrupted run resumes where it stopped.
#
# The pace is the publisher's own: one request a second, which is what the
# ministry's client limits itself to. At that rate this is a few hours.

set -u
cd "$(dirname "$0")"
LOG=collection.log
: > "$LOG"

declare -A EXPECTED=( [المستهلك]=430 [المنشأة]=1527 [المملكة]=3799 [النشاط]=6033 )

for term in المستهلك المنشأة المملكة النشاط; do
  echo "=== $term (expecting ${EXPECTED[$term]}) — $(date -u +%H:%M:%S) ===" >> "$LOG"
  for attempt in 1 2 3; do
    if python3 collect_judgments.py --term "$term" --max "${EXPECTED[$term]}" >> "$LOG" 2>&1; then
      break
    fi
    echo "  attempt $attempt failed; retrying in $((attempt * 30))s" >> "$LOG"
    sleep $((attempt * 30))
  done
done

echo "=== finished $(date -u +%H:%M:%S) ===" >> "$LOG"
wc -l judgments_*.jsonl >> "$LOG" 2>&1
