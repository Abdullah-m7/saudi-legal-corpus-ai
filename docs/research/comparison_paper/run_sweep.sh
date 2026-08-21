#!/bin/bash
# The sweep has twice exited early without an error or a traceback --- once
# after a single year. Rather than diagnose a process that leaves no evidence,
# make restarting free: the collector already skips a year whose file exists,
# so re-invoking it resumes exactly where it stopped. This loops until all 39
# year files are present or the attempt budget runs out.
cd "$(dirname "$0")"
for attempt in $(seq 1 40); do
  n=$(ls uk_collection/*.json 2>/dev/null | wc -l)
  if [ "$n" -ge 39 ]; then
    echo "ALL 39 YEARS COLLECTED (attempt $attempt)"
    exit 0
  fi
  echo "--- attempt $attempt, $n year files so far ---"
  python3 collect_uk.py --years 1988-2026
done
echo "gave up with $(ls uk_collection/*.json 2>/dev/null | wc -l) year files"
exit 1
