#!/usr/bin/env python3
"""Contemporary views of the corpus, defined from the corpus and from the
dates the judgments themselves give the reforms.

This project has been reading its corpus as a time series. That was the wrong
frame for the question that matters: what law is actually invoked in Saudi
adjudication *now*. So the primary object is a window on the recent years, and
history is used only where a recent reform makes a before/after design valid.

Four views. None is balanced, and none is made balanced, because balancing a
window on a corpus whose publication practice changed would be inventing
judgments. Each view reports its own composition instead, so a reader can see
what it is made of before believing anything measured on it.

  contemporary_5y   1442-1446
  contemporary_3y   1444-1446, the densest recent block
  post_Evidence     1443-1446, the Evidence Law being م/43 of 26/5/1443
  post_CTL          1445-1446, the Civil Transactions Law being م/191 of
                    29/11/1444, so 1445 is the first full year after it

Every decree number and date above is quoted from the judgments, not from
memory: `windows.py --decrees` prints the sentences the corpus writes them in.

    python3 windows.py            # composition of every view
    python3 windows.py --decrees  # what the judgments say the reforms are
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
SHARDS = sorted((HERE.parent / "arabic_paper" / "judgments").glob("*.jsonl"))
import voice_attribution as V         # noqa: E402

OUT = HERE / "windows_results.json"

# Reform dates, each attested in the corpus. The count is how many judgments
# write the decree number and date out in full beside the instrument's name.
REFORMS = {
    "commercial_courts_law": ("م/93", "15/08/1441", 847),
    "evidence_law": ("م/43", "26/05/1443", 107),
    "personal_status_law": ("م/73", "06/08/1443", 1),
    "civil_transactions_law": ("م/191", "29/11/1444", 28),
}

VIEWS = {
    "contemporary_5y": list(range(1442, 1447)),
    "contemporary_3y": list(range(1444, 1447)),
    "post_Evidence": list(range(1443, 1447)),
    "post_CTL": list(range(1445, 1447)),
}
# 1447 holds 90 judgments and 1448 holds 277. Those are not years, they are the
# leading edge of a collection still filling, and a rate computed on them would
# move for reasons that have nothing to do with law.
EXCLUDED_TAIL = [1447, 1448]

DECREE = re.compile(r"(نظام\s+[^\.،؛\n]{3,40}?)\s*(?:الصادر|صادر)[^\.،؛\n]{0,30}?"
                    r"رقم[:\s]*\(?\s*(م\s*/\s*[\d٠-٩]{1,4})\s*\)?"
                    r"[^\.،؛\n]{0,20}?تاريخ[:\s]*\(?\s*([\d٠-٩/\-\s]{6,20})")


def judgments():
    for shard in SHARDS:
        for line in shard.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def year_of(rec):
    y = str(rec.get("hijri_year") or "").strip()
    return int(y) if y.isdigit() else None


def profile(rec):
    """What a judgment contributes to a view's composition."""
    text = rec["text"]
    spans = V.segments(text, rec.get("sections") or {})
    lens = collections.Counter()
    for a, b, v in spans:
        lens[v] += b - a
    reasoned = lens["reasoning"] > 0
    return {
        "year": year_of(rec),
        "court": (rec.get("court") or "?").strip(),
        "courtType": rec.get("court_type") or "?",
        "isAppeal": str(rec.get("is_appeal")) == "True",
        "chars": len(text),
        "reasoned": reasoned,
        "reasoningChars": lens["reasoning"],
        "hasRecital": lens["recital"] > 0,
    }


def compose(profiles):
    n = len(profiles)
    if not n:
        return {}
    reasoned = sum(p["reasoned"] for p in profiles)
    rc = [p["reasoningChars"] for p in profiles if p["reasoned"]]
    rc.sort()
    return {
        "judgments": n,
        "withReasons": reasoned,
        "withReasonsShare": round(100 * reasoned / n, 1),
        "medianReasoningChars": rc[len(rc) // 2] if rc else 0,
        "byYear": dict(sorted(collections.Counter(
            p["year"] for p in profiles).items())),
        "byCourt": dict(collections.Counter(
            p["court"] for p in profiles).most_common(6)),
        "byCourtType": dict(collections.Counter(
            p["courtType"] for p in profiles).most_common()),
        "appellateShare": round(
            100 * sum(p["isAppeal"] for p in profiles) / n, 1),
    }


def decrees():
    seen = collections.Counter()
    for rec in judgments():
        for m in DECREE.finditer(rec["text"]):
            key = re.sub(r"\s+", " ", " ".join(m.groups())).strip()
            seen[key[:96]] += 1
    for k, n in seen.most_common(20):
        print(f"{n:>6}  {k}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--decrees", action="store_true")
    args = ap.parse_args()
    if args.decrees:
        return decrees()

    profiles = collections.defaultdict(list)
    allp = []
    for rec in judgments():
        p = profile(rec)
        allp.append(p)
        for name, years in VIEWS.items():
            if p["year"] in years:
                profiles[name].append(p)

    out = {"reforms": {k: {"decree": d, "date": t, "attestedInJudgments": n}
                       for k, (d, t, n) in REFORMS.items()},
           "excludedTailYears": EXCLUDED_TAIL,
           "wholeCorpus": compose(allp),
           "views": {k: compose(v) for k, v in profiles.items()}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print("reforms, as the judgments themselves date them")
    for k, (d, t, n) in REFORMS.items():
        print(f"  {k:<34}{d:>8}  {t}   written out in {n:,} judgments")
    print(f"\n{'view':<18}{'judgments':>11}{'with reasons':>14}{'(%)':>7}"
          f"{'median reasons':>16}{'appellate %':>13}")
    rows = [("whole corpus", out["wholeCorpus"])] + [
        (k, out["views"][k]) for k in VIEWS]
    for name, c in rows:
        print(f"{name:<18}{c['judgments']:>11,}{c['withReasons']:>14,}"
              f"{c['withReasonsShare']:>7.1f}{c['medianReasoningChars']:>16,}"
              f"{c['appellateShare']:>13.1f}")
    print("\ncomposition by year")
    for name in VIEWS:
        c = out["views"][name]
        years = " ".join(f"{y}:{n:,}" for y, n in c["byYear"].items())
        print(f"  {name:<18}{years}")
    print("\ncomposition by court, contemporary_3y")
    for k, v in out["views"]["contemporary_3y"]["byCourt"].items():
        print(f"  {v:>8,}  {k}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
