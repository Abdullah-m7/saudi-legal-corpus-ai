#!/usr/bin/env python3
"""The law-in-action functionality layer: one row per statutory article.

Not a normative hierarchy and not a ranking of importance. What this records
is how a provision behaves in published commercial adjudication -- what it
does when a court reaches for it, how often each voice reaches for it, and
what tends to appear beside it.

It supersedes nothing: `completeness_layer.csv` carries the taxonomy that was
tested and found PARTIAL, and it stays. This carries the partition that
replaced it, with the provenance of every label attached to the row rather
than buried in a README, because a categorical hand label without its
provenance is indistinguishable from a measurement.

    python3 article_function.py
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
FUNC = HERE / "adjudicative_function_gold.json"
FN13 = HERE / "function_labels.json"
OUT = HERE / "article_function.csv"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
MIN = 10
RECENT = {1444, 1445, 1446}


def main():
    gold = json.loads(FUNC.read_text(encoding="utf-8"))
    labels = gold["labels"]
    fn13 = json.loads(FN13.read_text(encoding="utf-8"))["labels"]
    docs = collections.defaultdict(
        lambda: {"c": collections.Counter(), "ca": set(), "pa": set(),
                 "y": 0})
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            a = ((r["inst"], r["art"]) if r.get("inst")
                 and r.get("art") is not None else None)
            if r["role"] == "court_reasoning":
                d["c"][r["t"]] += 1
                if a:
                    d["ca"].add(a)
            elif r["role"] in ("party_argument", "recital") and a:
                d["pa"].add(a)

    cn = collections.Counter(); hit = collections.Counter()
    fq = collections.Counter(); mx = collections.Counter()
    pn = collections.Counter(); c3 = collections.Counter()
    for d in docs.values():
        mixed = any(d["c"][t] for t in NONSTATUTE)
        for a in d["ca"]:
            cn[a] += 1
            if d["y"] in RECENT:
                c3[a] += 1
            if mixed:
                hit[a] += 1
            if d["c"]["fiqh_source"]:
                fq[a] += 1
            if d["c"]["legal_maxim"]:
                mx[a] += 1
        for a in d["pa"]:
            pn[a] += 1
    rank = {a: i + 1 for i, (a, _) in enumerate(
        sorted(c3.items(), key=lambda kv: (-kv[1], kv[0]))[:100])}

    rows = []
    for a in sorted(set(cn) | set(pn), key=lambda a: -cn[a]):
        if cn[a] < MIN and pn[a] < MIN:
            continue
        lab = labels.get(f"{a[0]}:{a[1]}")
        rows.append({
            "article_id": f"{a[0]}:{a[1]}",
            "instrument": a[0], "article": a[1],
            "function_class": (lab or {}).get("function", ""),
            "function_rule_label": (lab or {}).get("ruleLabel", ""),
            "function_ambiguous":
                "" if not lab else str(lab["ambiguous"]).lower(),
            "function_note": (lab or {}).get("note", ""),
            "subtype_descriptive":
                (fn13.get(f"{a[0]}:{a[1]}") or {}).get("function", ""),
            "completeness_class": (lab or {}).get("completenessClass", ""),
            "provenance": (
                "hand label, one reader, from enacted text and legal "
                "function; NOT blind to supplementation rates; sensitivity "
                "label in function_rule_label is a mechanical map from "
                "function.py, assigned before any rate existed"
                if lab else
                "outside the classified frame (fewer than 30 court-citing "
                "judgments in 1442-1446)"),
            "operational_core_rank_3y": rank.get(a, ""),
            "court_judgments": cn[a],
            "party_judgments": pn[a],
            "hybrid_rate": round(100 * hit[a] / cn[a], 1) if cn[a] else "",
            "named_fiqh_rate": round(100 * fq[a] / cn[a], 1) if cn[a] else "",
            "maxim_rate": round(100 * mx[a] / cn[a], 1) if cn[a] else "",
            "window": "contemporary_5y (1442-1446); rank column is 1444-1446",
        })
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    lab = sum(1 for r in rows if r["function_class"])
    print(f"{len(rows)} articles, {lab} carrying a function class -> {OUT.name}")


if __name__ == "__main__":
    main()
