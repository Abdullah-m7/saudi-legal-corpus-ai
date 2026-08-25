#!/usr/bin/env python3
"""Rebuild every judgments_*.jsonl from the cache, with one counting rule.

The morphological count was fixed while the collection was already running,
so the term collected first carries the old literal count and the rest carry
the new one. Four files produced by two different rules is not a dataset.

This reads the cached detail records - the raw material, untouched by either
version - and writes all four files again through the same code. Run it once
the collection finishes.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collect_judgments import CACHE, HERE, TEXT_FIELDS, occurrences, plain

TERMS = ["المستهلك", "المنشأة", "المملكة", "النشاط"]


def body_of(record):
    return " ".join(plain(record.get(f)) for f in TEXT_FIELDS).strip()


def main():
    cached = {}
    for path in CACHE.glob("*.json"):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  unreadable cache file, skipped: {path.name}")
            continue
        cached[d.get("id") or path.stem] = d
    print(f"{len(cached)} judgments in the cache")

    for term in TERMS:
        slug = re.sub(r'[\\/:*?"<>|\s]+', "_", term).strip("_")
        src = HERE / f"judgments_{slug}.jsonl"
        if not src.exists():
            print(f"  {term}: not collected yet")
            continue
        rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
        changed = 0
        for r in rows:
            d = cached.get(r["id"])
            body = body_of(d) if d else r.get("text", "")
            n = occurrences(body, term)
            if n != r.get("occurrences"):
                changed += 1
            r["occurrences"], r["text"], r["characters"] = n, body, len(body)
        with src.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        zeros = sum(1 for r in rows if r["occurrences"] == 0)
        print(f"  {term}: {len(rows)} rows, {changed} counts corrected, "
              f"{zeros} still zero")


if __name__ == "__main__":
    main()
