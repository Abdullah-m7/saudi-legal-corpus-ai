#!/usr/bin/env python3
"""The GSTC_TEST2 result, reported the way a reader has to read it.

`evaluate.py` gives one accuracy per stage. That is not enough to say what
the system is for. A system that prefers an explicit gap to a wrong
instrument has two different numbers -- how often it answers, and how often
it is right when it does -- and collapsing them into one hides the property
that makes it usable. So this reports:

  detection precision and recall separately, because a set that is 92 per
  cent citations makes detection accuracy look like a good number when it is
  mostly the base rate;

  the UNRESOLVED RATE: gold citations where the instrument is recoverable and
  the parser declines to name one;

  selective accuracy: coverage, and accuracy on the covered part;

  the abstention breakdown -- wrong confident answer, correct abstention,
  unnecessary abstention -- because the first is the only one that misleads a
  reader of the output, and the other two do not deserve the same penalty;

  and the same numbers per document family and per subject, because a stratum
  drawn from one publication is a result about that publication.

    python3 report_test2.py [--set gstc_test2] [--json]
"""
import argparse, collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate                                          # noqa: E402
from evaluate import (SETS, documents_for, gazetteer_for, load_dev,
                      norm_paragraph, predict_at, wilson)  # noqa: E402
import grammar                                           # noqa: E402
from instruments import same as same_instrument          # noqa: E402


def pct(k, n):
    return f"{100*k/n:5.1f}  [{wilson(k, n)[0]}, {wilson(k, n)[1]}]" if n else "    -"


def collect(which):
    evaluate.DEV = SETS[which]
    spec = json.loads(SETS[which].read_text(encoding="utf-8"))
    stages = list(grammar.STAGES)
    gaz = gazetteer_for(documents_for(spec), None, (str(SETS[which]), "all"))
    rows = []
    for item, text, offset in load_dev(None):
        pred = predict_at(text, offset, stages, gaz)
        rows.append({"id": item["id"], "doc": item["doc"],
                     "gold": item["label"], "pred": pred})
    return spec, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="gstc_test2")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    spec, rows = collect(a.set)

    stratum_of = {}
    for name, alloc in spec.get("allocation", {}).items():
        for doc in alloc["documents"]:
            stratum_of[doc] = name

    # ---- detection, as precision and recall ------------------------------
    tp = sum(1 for r in rows if r["pred"] and r["gold"]["isCitation"])
    fp = sum(1 for r in rows if r["pred"] and not r["gold"]["isCitation"])
    fn = sum(1 for r in rows if not r["pred"] and r["gold"]["isCitation"])
    tn = sum(1 for r in rows if not r["pred"] and not r["gold"]["isCitation"])

    # ---- instrument: answered / abstained, right / wrong ------------------
    kinds = collections.Counter()
    for r in rows:
        g = r["gold"]
        if not g["isCitation"]:
            continue
        p = r["pred"]
        gold_has = bool(g["instrument"])
        said = bool(p and p.get("instrument"))
        if not p:
            kinds["missed the citation entirely"] += 1
        elif said and gold_has and same_instrument(p["instrument"], g["instrument"]):
            kinds["answered, right"] += 1
        elif said and gold_has:
            kinds["answered, wrong instrument"] += 1
        elif said and not gold_has:
            kinds["answered where the gold has none"] += 1
        elif not said and gold_has:
            kinds["abstained, unnecessarily"] += 1
        else:
            kinds["abstained, correctly"] += 1

    # a wrong instrument is not one thing. Either the parser named a
    # different instrument, or it named the right one and drew the span in
    # the wrong place. A reader would accept the second and be misled only by
    # the first, so they are counted apart.
    def fold(x):
        return "".join(c for c in (x or "") if c not in " \u0640")\
            .replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")\
            .replace("ة", "ه").replace("ى", "ي")

    span_only = 0
    for r in rows:
        g, p_ = r["gold"], r["pred"]
        if not (g["isCitation"] and g["instrument"] and p_ and p_.get("instrument")):
            continue
        if same_instrument(p_["instrument"], g["instrument"]):
            continue
        got, want = fold(p_["instrument"]), fold(g["instrument"])
        if got and want and (got.startswith(want) or want.startswith(got)):
            span_only += 1

    cited = [r for r in rows if r["gold"]["isCitation"]]
    resolvable = [r for r in cited if r["gold"]["instrument"]]
    unresolved = sum(1 for r in resolvable
                     if not (r["pred"] and r["pred"].get("instrument")))

    # ---- selective accuracy on the full answer ---------------------------
    def exact(r):
        g, p = r["gold"], r["pred"]
        if not p:
            return False
        if p["articleNumber"] != g["articleNumber"]:
            return False
        if norm_paragraph(p["paragraph"]) != norm_paragraph(g["paragraph"]):
            return False
        if bool(p.get("instrument")) != bool(g["instrument"]):
            return False
        if g["instrument"] and not same_instrument(p["instrument"], g["instrument"]):
            return False
        return True

    answered = [r for r in cited if r["pred"] and r["pred"].get("instrument")]
    covered_right = sum(1 for r in answered if exact(r))
    all_right = sum(1 for r in cited if exact(r))

    out = {
        "set": a.set, "items": len(rows), "goldCitations": len(cited),
        "detection": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "abstention": dict(kinds),
        "wrongSpanOnly": span_only,
        "unresolvedRate": round(100 * unresolved / max(1, len(resolvable)), 1),
        "coverage": round(100 * len(answered) / max(1, len(cited)), 1),
        "accuracyWhenAnswered": round(100 * covered_right / max(1, len(answered)), 1),
        "accuracyOverall": round(100 * all_right / max(1, len(cited)), 1),
    }

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    print(f"set: {a.set}   {len(rows)} items, {len(cited)} gold citations\n")
    print("DETECTION")
    print(f"  precision      {tp}/{tp+fp}   {pct(tp, tp+fp)}")
    print(f"  recall         {tp}/{tp+fn}   {pct(tp, tp+fn)}")
    print(f"  true negatives {tn}/{tn+fp}   {pct(tn, tn+fp)}")
    print("\nINSTRUMENT, BY WHAT THE PARSER DID")
    for k in ("answered, right", "answered, wrong instrument",
              "answered where the gold has none", "abstained, correctly",
              "abstained, unnecessarily", "missed the citation entirely"):
        if kinds[k]:
            print(f"  {k:38} {kinds[k]:4}   {100*kinds[k]/len(cited):5.1f}%")
        if k == "answered, wrong instrument" and kinds[k]:
            print(f"  {'   of which: right name, wrong span':38} {span_only:4}"
                  f"   {100*span_only/len(cited):5.1f}%")
            print(f"  {'   of which: a different instrument':38} "
                  f"{kinds[k] - span_only:4}"
                  f"   {100*(kinds[k]-span_only)/len(cited):5.1f}%")
    print(f"\n  UNRESOLVED RATE {unresolved}/{len(resolvable)} = {out['unresolvedRate']}%"
          "   (gold names an instrument, parser declines)")
    print("\nSELECTIVE ACCURACY  (article + paragraph + instrument all right)")
    print(f"  coverage                {out['coverage']}%   "
          f"({len(answered)} of {len(cited)} citations answered)")
    print(f"  accuracy when answered  {out['accuracyWhenAnswered']}%   {pct(covered_right, len(answered))}")
    print(f"  accuracy over all       {out['accuracyOverall']}%   {pct(all_right, len(cited))}")

    print("\nBY STRATUM")
    print(f"  {'stratum':24}{'n':>5}{'exact':>8}{'coverage':>10}{'when answered':>15}")
    by = collections.defaultdict(list)
    for r in cited:
        by[stratum_of.get(r["doc"], "?")].append(r)
    for name, rs in sorted(by.items()):
        ans = [r for r in rs if r["pred"] and r["pred"].get("instrument")]
        ex = sum(1 for r in rs if exact(r))
        exa = sum(1 for r in ans if exact(r))
        print(f"  {name:24}{len(rs):5}{100*ex/len(rs):7.1f}%"
              f"{100*len(ans)/len(rs):9.1f}%{(100*exa/len(ans) if ans else 0):14.1f}%")

    print("\nBY DOCUMENT")
    print(f"  {'document':38}{'n':>5}{'exact':>8}{'coverage':>10}")
    byd = collections.defaultdict(list)
    for r in cited:
        byd[r["doc"]].append(r)
    for name, rs in sorted(byd.items(), key=lambda kv: -len(kv[1])):
        ans = [r for r in rs if r["pred"] and r["pred"].get("instrument")]
        ex = sum(1 for r in rs if exact(r))
        print(f"  {name:38}{len(rs):5}{100*ex/len(rs):7.1f}%{100*len(ans)/len(rs):9.1f}%")

    print("\nBY SEGMENT (gold)")
    print(f"  {'segment':24}{'n':>5}{'exact':>8}{'segment right':>15}")
    bys = collections.defaultdict(list)
    for r in cited:
        bys[r["gold"]["segment"] or "?"].append(r)
    for name, rs in sorted(bys.items(), key=lambda kv: -len(kv[1])):
        ex = sum(1 for r in rs if exact(r))
        seg = sum(1 for r in rs if r["pred"] and r["pred"].get("segment") == r["gold"]["segment"])
        print(f"  {name:24}{len(rs):5}{100*ex/len(rs):7.1f}%{100*seg/len(rs):14.1f}%")

    print("\nBY HOW THE INSTRUMENT IS RECOVERABLE (gold)")
    print(f"  {'instrumentSource':24}{'n':>5}{'instrument right':>18}")
    byi = collections.defaultdict(list)
    for r in cited:
        byi[r["gold"]["instrumentSource"] or "none"].append(r)
    for name, rs in sorted(byi.items(), key=lambda kv: -len(kv[1])):
        ok = sum(1 for r in rs if r["pred"] and r["pred"].get("instrument")
                 and r["gold"]["instrument"]
                 and same_instrument(r["pred"]["instrument"], r["gold"]["instrument"]))
        print(f"  {name:24}{len(rs):5}{100*ok/len(rs):17.1f}%")


if __name__ == "__main__":
    main()
