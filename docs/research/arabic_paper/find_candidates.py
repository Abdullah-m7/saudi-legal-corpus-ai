#!/usr/bin/env python3
"""Find judgments where a court construes a term AND resolves a conflict.

The census settled the idiom. These are the phrases the courts actually use,
with the ones they never use dropped: a judgment is a candidate when it
carries at least one phrase from each family, close enough together that the
two are plausibly about the same passage rather than two unrelated parts of a
long judgment.

Proximity, not co-occurrence in the document. A commercial judgment runs to
4,600 characters at the median and 96,000 at the longest; "تعريف" on page one
and "الترجيح" on page eight are not evidence of anything.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOW = 600  # characters between the two phrases

CONSTRUCTION = ["تعريف", "التعريف", "بمفهوم", "المقصود به", "مدلول",
                "بحسب تعريف", "عرّف", "في مفهوم", "عرفت المادة",
                "المقصود بـ", "بمدلول", "المراد بـ", "وفق تعريف"]
CONFLICT = ["تعارض", "التعارض", "ترجيح", "الترجيح", "العام والخاص",
            "الخاص يقيد العام", "يقيد العام", "النص الخاص", "النص العام",
            "التخصيص", "اللاحق ينسخ"]

C_RE = re.compile("|".join(map(re.escape, CONSTRUCTION)))
K_RE = re.compile("|".join(map(re.escape, CONFLICT)))


def passages(text):
    """Spans where a construction phrase and a conflict phrase are close."""
    cons = [(m.start(), m.group()) for m in C_RE.finditer(text)]
    conf = [(m.start(), m.group()) for m in K_RE.finditer(text)]
    if not cons or not conf:
        return []
    out = []
    for ci, cw in cons:
        for ki, kw in conf:
            if abs(ci - ki) <= WINDOW:
                a, b = min(ci, ki), max(ci, ki)
                out.append({"construction": cw, "conflict": kw,
                            "gap": abs(ci - ki),
                            "passage": " ".join(
                                text[max(0, a - 250):b + 350].split())})
                break
    return out


def main():
    found = []
    total = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            total += 1
            ps = passages(r["text"])
            if ps:
                found.append({
                    "id": r["id"], "judgment_number": r["judgment_number"],
                    "court": r["court"], "city": r["city"],
                    "hijri_date": r["hijri_date"],
                    "characters": r["characters"],
                    "pairs": len(ps), "passages": ps[:4],
                })
    found.sort(key=lambda r: -r["pairs"])
    out = HERE / "definition_conflict_candidates.json"
    out.write_text(json.dumps(
        {"scanned": total, "window_characters": WINDOW,
         "construction_phrases": CONSTRUCTION, "conflict_phrases": CONFLICT,
         "candidates": len(found), "records": found},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"scanned {total:,} judgments")
    print(f"{len(found):,} carry a construction phrase within {WINDOW} "
          f"characters of a conflict phrase ({len(found)/total:.2%})")
    import collections
    print("by court:", dict(collections.Counter(r["court"] for r in found)))
    print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
