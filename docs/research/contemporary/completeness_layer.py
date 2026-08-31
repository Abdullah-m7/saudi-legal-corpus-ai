#!/usr/bin/env python3
"""The derived layer this programme exists to leave behind.

One row per statutory article that the bench actually cites often enough to
measure, carrying what the article IS (from its enacted text, classified by
hand and blind) beside what happens WHEN IT IS CITED (from the mention
layer). That join is the thing no other artefact in the repository can do,
and it is what lets a later question be a scan rather than a re-derivation:

    which enacted provisions systematically require courts to reason
    beyond their text?

Deliberately NOT a completeness score. The class is a hand judgment by one
reader from the article's words, it is categorical, and it stays categorical;
`classification` records who made it and how far it has been checked. A
numeric score would imply an ordering between INSTITUTIONAL_DIRECTIVE and
DEFINITION_STATUS that nothing here establishes.

    python3 completeness_layer.py
"""
import collections
import csv
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
LAYER = HERE / "authority_mentions.jsonl.gz"
GOLD = HERE / "completeness_gold.json"
CORE = HERE / "core_view.json"
OUT = HERE / "completeness_layer.csv"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
MIN_TIER2 = 10


def scan(roles):
    docs = collections.defaultdict(
        lambda: [collections.Counter(), set()])
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["role"] not in roles:
                continue
            d = docs[r["j"]]
            d[0][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[1].add((r["inst"], r["art"]))
    n = collections.Counter()
    hit = collections.Counter()
    fiqh = collections.Counter()
    for types, arts in docs.values():
        mixed = any(types[t] for t in NONSTATUTE)
        for a in arts:
            n[a] += 1
            if mixed:
                hit[a] += 1
            if types["fiqh_source"]:
                fiqh[a] += 1
    return n, hit, fiqh


def main():
    gold = json.loads(GOLD.read_text(encoding="utf-8"))["labels"]
    core = json.loads(CORE.read_text(encoding="utf-8"))
    rank = {}
    for r in core["views"]["contemporary_3y"]["top50"]:
        rank[(r["instrument"], r["article"])] = r["rank"]
    cn, ch, cf = scan({"court_reasoning"})
    pn, ph, _ = scan({"party_argument", "recital"})

    rows = []
    for a in sorted(cn, key=lambda a: -cn[a]):
        if cn[a] < MIN_TIER2:
            continue
        lab = gold.get(f"{a[0]}:{a[1]}")
        rows.append({
            "article_id": f"{a[0]}:{a[1]}",
            "instrument": a[0],
            "article": a[1],
            "official_text_ref": "corpus_registry.json / tracks / "
                                 f"{a[0]} / article {a[1]}",
            "completeness_class": (lab or {}).get("class") or "",
            "classification": ("hand, one reader, blind to all rates; "
                               "INTERPRETIVE_LAYER"
                               if lab else "not classified: outside the "
                               "n>=30 frame"),
            "class_ambiguous": "" if not lab else str(lab["ambiguous"]).lower(),
            "rate_seen_before_classifying":
                "" if not lab else str(lab["ratePreviouslySeen"]).lower(),
            "court_judgments": cn[a],
            "court_nonstatutory_rate": round(100 * ch[a] / cn[a], 1),
            "court_named_fiqh_rate": round(100 * cf[a] / cn[a], 1),
            "party_judgments": pn[a],
            "party_nonstatutory_rate":
                round(100 * ph[a] / pn[a], 1) if pn[a] >= 20 else "",
            "operational_core_rank": rank.get(a, ""),
            "window": "contemporary_5y (1442-1446)",
        })
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    classified = sum(1 for r in rows if r["completeness_class"])
    print(f"{len(rows)} articles (>= {MIN_TIER2} court-citing judgments); "
          f"{classified} carry a completeness class")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
