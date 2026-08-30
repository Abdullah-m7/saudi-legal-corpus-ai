#!/usr/bin/env python3
"""Court and litigants inside the same judgment: the claim, and the tests it
has to survive.

The gate (`gate.py`, seed 71) validated the two things the claim rests on and
failed on a third. It found the bench's own reasons attributed correctly 12
times out of 12, the five contrasted type/voice cells clean 80 out of 80 --
and the *recital* mislabelled 5 times in 12, every one of them a party
pleading that carried no cue near the mention. So the cue-based party column
under-counts party speech, and four of the five missed ones were statute or
maxim, which is exactly the direction that could manufacture the result.

The response is not to patch the cue. It is to compute the contrast under two
specifications and report both:

  STRICT   party = a recital mention with a party cue near it. High precision,
           low recall: it is the speech the classifier is sure about.
  WIDE     party = every recital mention. The recital is where pleadings live,
           so this is high recall and low precision: it sweeps in the court's
           own narration of the facts.

The truth about party speech lies between them. A contrast that survives both
is not an artefact of either.

    python3 claim.py [--json]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import arabic_ordinals as AO          # noqa: E402
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "claim_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
SPECS = ("strict", "wide")


def side(m, spec):
    """court | party | None, under one specification."""
    v = A.voice(m)
    if v == "court_reasoning":
        return "court"
    if spec == "strict":
        return "party" if v == "party_argument" else None
    return "party" if m["segment"] == "recital" else None


def blank():
    return {
        "n": 0, "reasoned": 0,
        # A / B: type by side, per specification
        "byside": {s: collections.defaultdict(collections.Counter)
                   for s in SPECS},
        # C: the same, restricted
        "strat": collections.defaultdict(
            lambda: collections.defaultdict(collections.Counter)),
        # D: within-judgment transitions
        "trans": collections.Counter(), "partyMarg": collections.Counter(),
        "courtMarg": collections.Counter(), "pairedDocs": 0,
        # E: operational core, court reasoning only
        "core": collections.Counter(),
        # F: hybrid shapes
        "combo": collections.Counter(), "shape": collections.Counter(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    index, order = M.build(REGISTRY)
    acc = collections.defaultdict(blank)

    for rec in judgments():
        y = year_of(rec)
        keys = [n for n, ys in VIEWS.items() if y in ys]
        if y:
            keys.append(f"Y{y}")
        if not keys:
            continue
        text, sections = rec["text"], rec.get("sections") or {}
        ms = [m for m in A.mentions(text, sections, index, order)
              if not m.get("inQuote")]
        reasoned = any(A.voice(m) == "court_reasoning" for m in ms) or \
            any(v == "reasoning" for _, _, v in
                __import__("voice_attribution").segments(text, sections))

        court_types, party_types = set(), {s: set() for s in SPECS}
        for m in ms:
            for s in SPECS:
                sd = side(m, s)
                if sd == "party":
                    party_types[s].add(m["type"])
        for m in ms:
            if A.voice(m) == "court_reasoning":
                court_types.add(m["type"])

        has_stat = "statute" in court_types
        nonset = court_types & set(NONSTATUTE)

        for k in keys:
            b = acc[k]
            b["n"] += 1
            b["reasoned"] += reasoned
            for m in ms:
                t = m["type"]
                for s in SPECS:
                    sd = side(m, s)
                    if sd:
                        b["byside"][s][sd][t] += 1
                # C: strata. Only the strict spec, to keep the tables readable
                sd = side(m, "strict")
                if sd:
                    fam = "statutory" if t == "statute" else "non_statutory"
                    b["strat"][fam][sd][t] += 1
                    if t == "statute" and m["procedural"] is not None:
                        role = "procedural" if m["procedural"] else "substantive"
                        b["strat"][role][sd][t] += 1
                # E
                if A.voice(m) == "court_reasoning" and t == "statute" \
                        and m["instrument"]:
                    num, _ = AO.parse(m["article"] or "")
                    if num is not None:
                        b["core"][(m["instrument"], num)] += 1
            # D
            if court_types and party_types["strict"]:
                b["pairedDocs"] += 1
                for p in party_types["strict"]:
                    b["partyMarg"][p] += 1
                    for c in court_types:
                        b["trans"][(p, c)] += 1
                for c in court_types:
                    b["courtMarg"][c] += 1
            # F
            if reasoned:
                shape = ("hybrid" if has_stat and nonset else
                         "statute_only" if has_stat else
                         "non_statute_only" if nonset else "none")
                b["shape"][shape] += 1
                if shape == "hybrid":
                    for t in sorted(nonset):
                        b["combo"][t] += 1
                    b["combo"][("__ncombo__", len(nonset))] += 1
    return report(acc, args)


def shares(counter):
    tot = sum(counter.values()) or 1
    return {t: round(100 * counter[t] / tot, 2) for t in A.TYPES}, tot


def core_sizes(counter):
    tot = sum(counter.values()) or 1
    run, out, need = 0, {}, [50, 75, 90]
    for i, (_, v) in enumerate(counter.most_common(), 1):
        run += v
        while need and 100 * run / tot >= need[0]:
            out[f"articlesFor{need.pop(0)}pct"] = i
    for lvl in need:
        out[f"articlesFor{lvl}pct"] = None
    return out


def report(acc, args):
    out = {"views": {}, "byYear": {}}
    for k, b in acc.items():
        tgt = out["byYear"] if k.startswith("Y") else out["views"]
        row = {"judgments": b["n"], "reasoned": b["reasoned"]}
        for s in SPECS:
            cs, ct = shares(b["byside"][s]["court"])
            ps, pt = shares(b["byside"][s]["party"])
            row[f"{s}_court"] = cs
            row[f"{s}_party"] = ps
            row[f"{s}_courtN"] = ct
            row[f"{s}_partyN"] = pt
            row[f"{s}_ratio"] = {
                t: (round(ps[t] / cs[t], 2) if cs[t] else None) for t in A.TYPES}
        row["strata"] = {}
        for fam, sides in b["strat"].items():
            cs, ct = shares(sides["court"])
            ps, pt = shares(sides["party"])
            row["strata"][fam] = {"court": cs, "party": ps,
                                  "courtN": ct, "partyN": pt}
        n = sum(b["shape"].values()) or 1
        row["shape"] = {k2: round(100 * v / n, 1) for k2, v in b["shape"].items()}
        row["shapeN"] = dict(b["shape"])
        hy = b["shape"]["hybrid"] or 1
        row["hybridWith"] = {t: round(100 * b["combo"][t] / hy, 1)
                             for t in NONSTATUTE}
        row["hybridFamilies"] = {
            str(k2[1]): round(100 * v / hy, 1)
            for k2, v in b["combo"].items()
            if isinstance(k2, tuple) and k2[0] == "__ncombo__"}
        row["core"] = core_sizes(b["core"])
        row["coreTop"] = [[f"{a} art.{n2}", v]
                          for (a, n2), v in b["core"].most_common(10)]
        row["distinctArticles"] = len(b["core"])
        # D
        pd_ = b["pairedDocs"] or 1
        tr = {}
        for (p, c), v in b["trans"].most_common():
            exp = b["partyMarg"][p] * b["courtMarg"][c] / pd_
            tr[f"{p}->{c}"] = {"n": v, "expected": round(exp, 1),
                               "lift": round(v / exp, 2) if exp else None}
        row["pairedDocs"] = b["pairedDocs"]
        row["transitions"] = tr
        tgt[k] = row

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    v = out["views"]["contemporary_3y"]
    print("court against party, contemporary_3y, both specifications\n")
    print(f"{'type':<20}{'court':>9}{'party STRICT':>14}{'ratio':>8}"
          f"{'party WIDE':>13}{'ratio':>8}")
    for t in A.TYPES:
        w = out["views"]["contemporary_3y"]
        print(f"  {t:<18}{v['strict_court'][t]:>8.2f}%"
              f"{v['strict_party'][t]:>13.2f}%"
              f"{str(v['strict_ratio'][t]):>8}"
              f"{v['wide_party'][t]:>12.2f}%{str(v['wide_ratio'][t]):>8}")
    print(f"\n  mentions: court {v['strict_courtN']:,}, "
          f"party strict {v['strict_partyN']:,}, wide {v['wide_partyN']:,}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
