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

Not in the whole RECORD either. A published record can hold two judgments,
the first-instance one and the appeal, and this index is about what was
pleaded at first instance and what the court below did with it. So the plea
and the disposition are both read inside the first document, and the appeal
is reported separately rather than mixed in.

AND WHETHER IT SURVIVED
A cell reading «قُضي بعدم الاختصاص — الدفع أصاب» is worth little to a
practitioner who does not also know that the appeal court set that judgment
aside. Each entry now carries the appellate fate of its judgment, read from
the appellate operative part by ../arabic_paper/appellate_outcome.py.

The operative part is also matched on the text with its diacritics stripped:
«حَكَمَتِ الدَائِرَةُ» is fully vowelled in 584 judgments, and a plain-script
pattern reported every one of them as having no stated disposition.
"""

import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent / "arabic_paper"
SHARDS = sorted((ANALYSIS / "judgments").glob("*.jsonl"))
sys.path.insert(0, str(ANALYSIS))

import appellate_outcome as AO     # noqa: E402
import voice_attribution as V      # noqa: E402

APPEAL_AR = {"affirmed": "أُيِّد", "reversed": "نُقض أو أُلغي",
             "substituted": "أُلغي وحُكم مجددًا", "varied": "عُدِّل",
             "not_admitted": "لم يُقبل الاعتراض شكلًا",
             "other_disposition": "فُصل على وجهٍ آخر",
             "unclear": "لم يتبيّن من المنطوق",
             "no_appeal": "لا استئناف في السجلّ"}

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


def first_document(text, sections):
    """The first-instance judgment inside the record, as (start, end)."""
    spans = V.parts(text, sections)
    return spans[0] if spans else (0, len(text))


def operative_of(text, span):
    """The operative part inside one document, found despite vowelling."""
    a, b = span
    stripped, back = AO.bare_with_map(text[a:b])
    m = RULING.search(stripped)
    if not m:
        return None, None
    start = a + back[m.start()]
    return text[start:start + 1200], start


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
    survival = collections.defaultdict(collections.Counter)
    n = 0
    for shard in SHARDS:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            text = r["text"]
            span = first_document(text, r.get("sections"))
            op, at = operative_of(text, span)
            # the disposition is read from the ORIGINAL text: bare() folds
            # أ into ا, and «بإلزام» stops matching itself. Stripping is for
            # finding the operative part, not for reading it.
            decided = disposition(op)
            # the plea is a party's, so look for it before the disposition
            body = text[span[0]:at] if at else text[span[0]:span[1]]
            appeal_text = (r.get("sections") or {}).get("appealTextofRulling")
            appeal = AO.outcome(appeal_text)[0] if appeal_text else "no_appeal"
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
                    "appeal": appeal,
                    "appeal_ar": APPEAL_AR[appeal],
                })
                outcome[name][meaning] += 1
                survival[name][appeal] += 1
    HERE.mkdir(exist_ok=True)
    summary = []
    for name, rows in sorted(hits.items(), key=lambda kv: -len(kv[1])):
        slug = re.sub(r"\s+", "_", name)
        rows.sort(key=lambda e: (e["hijri_date"] or ""))
        (HERE / f"{slug}.json").write_text(json.dumps({
            "defence": name, "judgments": len(rows),
            "outcomes": dict(outcome[name]),
            "appeal": dict(survival[name]), "entries": rows,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        summary.append({"defence": name, "judgments": len(rows),
                        "share": round(len(rows) / n, 4),
                        "outcomes": dict(outcome[name]),
                        "appeal": dict(survival[name]),
                        "file": f"{slug}.json"})
        print(f"  {len(rows):>6,} ({len(rows)/n:>5.1%})  {name}")
        for k, v in outcome[name].most_common():
            print(f"          {v:>6,}  {k}")
    (HERE / "index.json").write_text(json.dumps(
        {"judgments_searched": n, "defences": summary},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{n:,} judgments searched; wrote {len(summary)} defence files")


if __name__ == "__main__":
    main()
