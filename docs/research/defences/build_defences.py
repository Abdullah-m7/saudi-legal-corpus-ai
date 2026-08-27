#!/usr/bin/env python3
"""What is pleaded before the Saudi commercial courts, and how it ends.

A drafting lawyer's second question, after how a provision has been applied,
is what the other side will say and how the court has handled it. This indexes
the preliminary and substantive defences raised across 50,666 judgments.

ON OUTCOMES, AND WHY MOST ARE LEFT BLANK
Matching outcome language does not work here. «رد الدفع» appears in 418
judgments and «قبول الدفع» in 180 — under one per cent between them. Courts
mostly do not announce that they accepted or rejected a plea; they rule and
move on. A tool that guessed from the surrounding prose would be inventing
holdings, which is the one thing this project will not do.

So the outcome is read only from the operative part — the text after «حكمت
الدائرة» — and only where it states the disposition in terms that decide the
plea on its face:

    a ruling of عدم الاختصاص settles a jurisdiction plea, and only that plea
    a ruling of عدم قبول الدعوى settles an admissibility plea, and only that
    a ruling on the merits (إلزام / رفض الدعوى) means the case was heard, which
      is informative for every preliminary plea in it

The disposition must MATCH the plea. A judgment that mentions عدم الاختصاص and
ends in عدم قبول الدعوى says nothing about the jurisdiction plea — it may have
been rejected, or never reached. A first version of this script filled that
cell anyway, which would have told a practitioner that 552 jurisdiction pleas
were resolved by an admissibility ruling. They were not. Those now read
«قُضي بغير ذلك».

Everything else is «لم يُصرَّح» — not stated. That column is mostly empty and
should be: an honest blank is worth more than a guess a practitioner relies on.

WHERE THE PLEA IS LOOKED FOR
Not in the whole judgment. A ruling of عدم الاختصاص contains that phrase in
its own operative part whether or not anyone pleaded it, so searching the
whole text counts the court's disposition as a party's plea. Detection stops
at حكمت الدائرة.
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent / "arabic_paper"
SHARDS = sorted((ANALYSIS / "judgments").glob("*.jsonl"))

DEFENCES = {
    "عدم الاختصاص": r"عدم\s+(?:ال)?اختصاص",
    "عدم قبول الدعوى": r"عدم\s+قبول\s+الدعوى",
    "سبق الفصل": r"سبق\s+الفصل|سابق\s+الفصل",
    "انعدام الصفة": r"انتفاء\s+الصفة|عدم\s+الصفة|انعدام\s+الصفة",
    "البطلان": r"بطلان\s+(?:العقد|الاتفاقية|الإجراء|الحكم|التبليغ)",
    "التقادم وسقوط الحق": r"سقوط\s+الحق|مضي\s+المدة|التقادم",
    "شرط التحكيم": r"شرط\s+التحكيم|وجود\s+شرط\s+تحكيم",
    "انعدام المصلحة": r"انتفاء\s+المصلحة|عدم\s+المصلحة",
}
RULING = re.compile(r"حكمت\s+الدائرة")

# Dispositions that settle a preliminary plea on their face.
OPERATIVE = [
    ("عدم الاختصاص", re.compile(r"عدم\s+(?:ال)?اختصاص")),
    ("عدم قبول الدعوى", re.compile(r"عدم\s+قبول\s+الدعوى")),
    ("موضوع", re.compile(r"بإلزام|إلزام\s+المدع|برفض\s+الدعوى|رفض\s+دعوى")),
]
MERITS = "فُصل في الموضوع — لم يوقف الدفعُ الشكلي نظرَ الدعوى"
NOT_STATED = "لم يُصرَّح في المنطوق"
OTHERWISE = "قُضي بغير ذلك — لا يفيد في هذا الدفع"
BEFORE, AFTER = 200, 300


def operative_of(text):
    m = RULING.search(text)
    return text[m.start():m.start() + 1200] if m else None


def disposition(op):
    """What the operative part decided, or None."""
    if not op:
        return None
    for label, pat in OPERATIVE:
        if pat.search(op):
            return label
    return None


def outcome_for(defence, decided):
    """Only a disposition that matches the plea settles it."""
    if decided is None:
        return NOT_STATED
    if decided == "موضوع":
        return MERITS
    if decided == defence:
        return f"قُضي بـ{defence} — الدفع أصاب"
    return OTHERWISE


def main():
    pats = {k: re.compile(v) for k, v in DEFENCES.items()}
    hits = collections.defaultdict(list)
    outcome = collections.defaultdict(collections.Counter)
    n = 0
    for shard in SHARDS:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            text = r["text"]
            op = operative_of(text)
            decided = disposition(op)
            # the plea is a party's, so look for it before the disposition
            k = RULING.search(text)
            body = text[:k.start()] if k else text
            for name, pat in pats.items():
                m = pat.search(body)
                if not m:
                    continue
                meaning = outcome_for(name, decided)
                a = max(0, m.start() - BEFORE)
                b = min(len(body), m.end() + AFTER)
                hits[name].append({
                    "judgment_id": r["id"],
                    "judgment_number": r["judgment_number"],
                    "court": r["court"], "city": r["city"],
                    "hijri_date": r["hijri_date"],
                    "passage": " ".join(body[a:b].split()),
                    "operative": " ".join(op.split())[:400] if op else None,
                    "outcome": meaning,
                })
                outcome[name][meaning] += 1
    HERE.mkdir(exist_ok=True)
    summary = []
    for name, rows in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        slug = re.sub(r"\s+", "_", name)
        rows.sort(key=lambda e: (e["hijri_date"] or ""))
        (HERE / f"{slug}.json").write_text(json.dumps({
            "defence": name, "judgments": len(rows),
            "outcomes": dict(outcome[name]), "entries": rows,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        summary.append({"defence": name, "judgments": len(rows),
                        "share": round(len(rows) / n, 4),
                        "outcomes": dict(outcome[name]), "file": f"{slug}.json"})
        print(f"  {len(rows):>6,} ({len(rows)/n:>5.1%})  {name}")
        for k, v in outcome[name].most_common():
            print(f"          {v:>6,}  {k}")
    (HERE / "index.json").write_text(json.dumps(
        {"judgments_searched": n, "defences": summary},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{n:,} judgments searched; wrote {len(summary)} defence files")


if __name__ == "__main__":
    main()
