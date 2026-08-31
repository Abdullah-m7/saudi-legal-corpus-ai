#!/usr/bin/env python3
"""Decomposing the 79.7 per cent: how much is the judicial office?

The manuscript's sharpest number is that in 79.7 per cent of judgments where
both sides are identified, they cite no article in common. The obvious
objection is that a court decides jurisdiction whether or not jurisdiction was
argued, and the consequences of absence whether or not absence was pleaded --
so the articles the bench "adds" may be its office rather than a disagreement.

This recomputes the overlap after removing that law, at six levels, and
reports the answer as a BAND rather than a point, because the function
taxonomy has a real ambiguous residual (`function_gold.json`) and forcing it
would manufacture precision.

    LOWER bound   exclude articles classified STRUCTURAL_PROCEDURAL
    UPPER bound   exclude STRUCTURAL_PROCEDURAL and AMBIGUOUS both

    python3 overlap.py
"""
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYER = HERE / "authority_mentions.jsonl.gz"
FN = json.loads((HERE / "function_labels.json").read_text(encoding="utf-8"))["labels"]
OUT = HERE / "overlap_results.json"
YEARS3 = {1444, 1445, 1446}


def klass(inst, art):
    return (FN.get(f"{inst}:{art}") or {}).get("class", "AMBIGUOUS")


def load(spec):
    """judgment -> {court/party: {level: set}}"""
    doc = collections.defaultdict(lambda: collections.defaultdict(set))
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["y"] not in YEARS3:
                continue
            if r["role"] == "court_reasoning":
                sd = "court"
            elif spec == "strict" and r["role"] == "party_argument":
                sd = "party"
            elif spec == "wide" and r["role"] in ("party_argument", "recital"):
                sd = "party"
            else:
                continue
            d = doc[r["j"]]
            d[f"{sd}_fam"].add(r["t"])
            if r.get("inst"):
                k = klass(r["inst"], r.get("art"))
                d[f"{sd}_inst_all"].add(r["inst"])
                if r.get("art") is not None:
                    d[f"{sd}_art_all"].add((r["inst"], r["art"]))
                    if k != "STRUCTURAL_PROCEDURAL":
                        d[f"{sd}_art_nostruct"].add((r["inst"], r["art"]))
                        d[f"{sd}_inst_nostruct"].add(r["inst"])
                    if k == "DISPUTE_SPECIFIC":
                        d[f"{sd}_art_dispute"].add((r["inst"], r["art"]))
                        d[f"{sd}_inst_dispute"].add(r["inst"])
    return doc


def measure(doc, key):
    vals, zero, exact = [], 0, 0
    for d in doc.values():
        a, b = d.get(f"court_{key}", set()), d.get(f"party_{key}", set())
        if not a or not b:
            continue
        vals.append(len(a & b) / len(a | b))
        zero += not (a & b)
        exact += a == b
    if not vals:
        return None
    vals.sort()
    n = len(vals)
    return {"n": n,
            "medianJaccard": round(vals[n // 2], 3),
            "meanJaccard": round(sum(vals) / n, 3),
            "p25": round(vals[n // 4], 3), "p75": round(vals[3 * n // 4], 3),
            "noOverlapPct": round(100 * zero / n, 1),
            "exactMatchPct": round(100 * exact / n, 1)}


LEVELS = [
    ("F. authority family", "fam"),
    ("D. instrument, all", "inst_all"),
    ("D. instrument, no structural", "inst_nostruct"),
    ("D. instrument, dispute-specific only", "inst_dispute"),
    ("A. article, all", "art_all"),
    ("B. article, no structural", "art_nostruct"),
    ("C. article, dispute-specific only", "art_dispute"),
]


# --------------------------------------------------------------- PHASE 3
def conditional(spec="strict"):
    """P(shared article | shared instrument), overall and per instrument.

    This separates two phenomena that the article-level figure alone cannot:
    the two sides reasoning from different CODES, and the two sides reasoning
    from the same code at different PROVISIONS. They are not the same fact
    about a legal system.
    """
    doc = collections.defaultdict(lambda: collections.defaultdict(set))
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["y"] not in YEARS3:
                continue
            if r["role"] == "court_reasoning":
                sd = "court"
            elif spec == "strict" and r["role"] == "party_argument":
                sd = "party"
            elif spec == "wide" and r["role"] in ("party_argument", "recital"):
                sd = "party"
            else:
                continue
            if r.get("inst") and r.get("art") is not None:
                doc[r["j"]][sd].add((r["inst"], r["art"]))
    both = shared_inst = shared_art = 0
    per = collections.defaultdict(lambda: {"shared": 0, "sameArt": 0})
    for d in doc.values():
        a, b = d.get("court", set()), d.get("party", set())
        if not a or not b:
            continue
        both += 1
        ia, ib = {x[0] for x in a}, {x[0] for x in b}
        common = ia & ib
        if common:
            shared_inst += 1
            if a & b:
                shared_art += 1
            for inst in common:
                per[inst]["shared"] += 1
                if {x for x in a if x[0] == inst} & {x for x in b if x[0] == inst}:
                    per[inst]["sameArt"] += 1
    print(f"\n[{spec}] both sides cite a statute: {both:,} judgments")
    print(f"  P(shared instrument | both cite statute) = "
          f"{100*shared_inst/both:.1f}%   ({shared_inst:,})")
    print(f"  P(shared article   | shared instrument) = "
          f"{100*shared_art/shared_inst:.1f}%   ({shared_art:,})")
    print(f"  P(shared article   | both cite statute) = "
          f"{100*shared_art/both:.1f}%")
    print(f"\n  {'instrument':<44}{'judgments':>11}{'same article':>14}")
    rows = {}
    for inst, d in sorted(per.items(), key=lambda kv: -kv[1]["shared"]):
        if d["shared"] < 30:
            continue
        pct = 100 * d["sameArt"] / d["shared"]
        rows[inst] = {"judgmentsSharingInstrument": d["shared"],
                      "sameArticlePct": round(pct, 1)}
        print(f"    {inst:<42}{d['shared']:>11,}{pct:>13.1f}%")
    return {"bothCiteStatute": both,
            "sharedInstrumentPct": round(100 * shared_inst / both, 1),
            "sharedArticleGivenInstrumentPct": round(100 * shared_art / shared_inst, 1),
            "sharedArticleGivenStatutePct": round(100 * shared_art / both, 1),
            "byInstrument": rows}


def main():
    res = {"_bands": "B is the LOWER bound of structural exclusion, C the"
                     " UPPER: the ambiguous residual is excluded in C and"
                     " retained in B.",
           "specs": {}}
    for spec in ("strict", "wide"):
        doc = load(spec)
        res["specs"][spec] = {k: measure(doc, k) for _, k in LEVELS}
        print(f"\n[{spec}]  contemporary_3y")
        print(f"{'level':<40}{'n':>7}{'median J':>10}{'p25':>7}{'p75':>7}"
              f"{'no overlap':>12}{'exact':>8}")
        for label, k in LEVELS:
            m = res["specs"][spec][k]
            if not m:
                print(f"  {label:<38}{'-':>7}")
                continue
            print(f"  {label:<38}{m['n']:>7,}{m['medianJaccard']:>10.3f}"
                  f"{m['p25']:>7.3f}{m['p75']:>7.3f}"
                  f"{m['noOverlapPct']:>11.1f}%{m['exactMatchPct']:>7.1f}%")
    # PHASE 3 is part of the same result file: reading the article-level
    # figure without the conditional invites the wrong reading of it, and a
    # separate run that has to be remembered is a figure that goes stale.
    res["conditional"] = {spec: conditional(spec)
                          for spec in ("strict", "wide")}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
