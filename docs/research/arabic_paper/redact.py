#!/usr/bin/env python3
"""Mask the personal identifiers the publisher's own redaction missed.

legislation is public; a judgment is public too - the ministry publishes
every one of these on its own site, with names and identifiers replaced by
(...). It does that 869,183 times across 98.4% of the corpus. But not
everywhere. A scan of all 50,666 judgments found:

    73  national ID or civil-registry numbers stated next to a full name
   122  mobile numbers, some belonging to named lawyers and arbitrators
   194  email addresses, mostly institutional court addresses

and in at least one judgment the identity number is redacted while the
mobile number two words later is not.

Republishing in bulk is not the same act as the ministry publishing each
judgment on its own page. Aggregated, downloadable and permanent, a leak the
publisher made once becomes a leak anyone can grep. So this masks what the
publisher intended to mask, using the publisher's own marker.

WHAT IS MASKED, AND WHAT IS NOT
  masked    a 10-digit number introduced by هوية / سجل مدني / إقامة
  masked    every 05xxxxxxxx mobile number
  masked    email addresses outside moj.gov.sa
  kept      bare 10-digit numbers with no identifying context: most are
            commercial-registration numbers, which are public by design, and
            a number attached to no name identifies nobody
  kept      court email addresses at moj.gov.sa, which are institutional
  kept      names themselves - they are what the ministry chose to publish

Every masked span is replaced by (...), the marker already used 869,183
times in this corpus, so a reader cannot tell our redaction from theirs and
no new convention is invented.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARDS = HERE / "judgments"
MARK = "(...)"

ID_CONTEXT = re.compile(
    r"((?:هوية|الهوية|هويه|سجل مدني|السجل المدني|سجلها المدني|سجله المدني|"
    r"إقامة|الإقامة|اقامة)[^0-9]{0,25})([12]\d{9})(?!\d)")
MOBILE = re.compile(r"(?<!\d)(05\d{8})(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@(?!moj\.gov\.sa)[\w-]+\.[\w.]+")


def scrub(text):
    if not text:
        return text, 0
    n = 0
    text, k = ID_CONTEXT.subn(lambda m: m.group(1) + MARK, text); n += k
    text, k = MOBILE.subn(MARK, text); n += k
    text, k = EMAIL.subn(MARK, text); n += k
    return text, n


def main():
    files = sorted(SHARDS.glob("*.jsonl"))
    total = changed_docs = changed_spans = 0
    for path in files:
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        touched = False
        for r in rows:
            total += 1
            hits = 0
            for key, value in list(r.get("sections", {}).items()):
                new, k = scrub(value)
                if k:
                    r["sections"][key] = new
                hits += k
            new, k = scrub(r["text"])
            hits += k
            if hits:
                r["text"] = new
                r["characters"] = len(new)
                r["provenance"]["transformation"] += (
                    f"; {hits} personal identifiers the publisher left "
                    f"unredacted were masked with its own {MARK} marker")
                changed_docs += 1
                changed_spans += hits
                touched = True
        if touched:
            with path.open("w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"scanned {total:,} judgments in {len(files)} shards")
    print(f"masked {changed_spans:,} identifiers across {changed_docs:,} judgments")


if __name__ == "__main__":
    main()
