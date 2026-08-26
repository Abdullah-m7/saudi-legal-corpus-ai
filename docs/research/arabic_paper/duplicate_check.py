#!/usr/bin/env python3
"""Are judgments published more than once under different numbers?

Three candidate passages turned out to be the same text under judgment
numbers 4430428479, 4430660137 and one more. Either the corpus duplicated
something during collection - it did not, every id is unique - or the
ministry publishes the same judgment under more than one number.

Hashes the normalised text of all 50,666 and reports texts that appear more
than once, with the numbers they appear under.
"""

import collections
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    seen = collections.defaultdict(list)
    total = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            total += 1
            text = re.sub(r"\s+", " ", r["text"]).strip()
            if len(text) < 500:      # very short texts collide meaninglessly
                continue
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            seen[h].append((r["judgment_number"], r["court"], r["hijri_date"]))

    dups = {h: v for h, v in seen.items() if len(v) > 1}
    copies = sum(len(v) for v in dups.values())
    print(f"{total:,} judgments, {len(seen):,} texts of 500+ characters")
    print(f"{len(dups):,} texts appear more than once, "
          f"accounting for {copies:,} records "
          f"({copies/total:.2%} of the corpus)")
    if dups:
        worst = sorted(dups.items(), key=lambda kv: -len(kv[1]))[:5]
        print("\nmost-repeated texts:")
        for h, v in worst:
            nums = ", ".join(n for n, _, _ in v[:6])
            print(f"  {len(v)}x  {v[0][1]}  →  {nums}")
    out = HERE / "duplicate_texts.json"
    out.write_text(json.dumps(
        {"judgments": total, "distinct_texts": len(seen),
         "repeated_texts": len(dups), "records_involved": copies,
         "groups": [{"copies": len(v), "records": v} for v in
                    sorted(dups.values(), key=len, reverse=True)]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out.name}")


if __name__ == "__main__":
    main()
