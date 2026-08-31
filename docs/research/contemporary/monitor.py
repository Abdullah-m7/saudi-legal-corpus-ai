#!/usr/bin/env python3
"""The contemporary monitoring view, and the delta between two releases.

MONITORING.md fixes the contract a new batch of judgments must pass. This is
the measurement half of it: one command that computes everything a release
needs to answer the questions this project has learned to ask, and one that
diffs two of those files.

The metric set is chosen from what went wrong before. A single denominator
made fiqh look like it was disappearing when it was not, so all five are here.
A citation-weighted average let art. 16 speak for the statute book, so the
article-level view is here too. And composition is printed first, because a
change in what gets published can produce every other delta on its own.

    python3 monitor.py                          # write the current view
    python3 monitor.py --delta <old view.json>  # report what moved
"""
import argparse
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                        # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
DOCS = HERE / "authority_layer.jsonl.gz"
FUNC = HERE / "adjudicative_function_gold.json"
OUT = HERE / "monitor_view.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
YEARS = (1442, 1443, 1444, 1445, 1446)
RECENT = {1444, 1445, 1446}


def build():
    fn = json.loads(FUNC.read_text(encoding="utf-8"))["labels"]
    reasoned = collections.Counter()
    total = collections.Counter()
    with gzip.open(DOCS, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r:
                continue
            total[r["year"]] += 1
            if r.get("reasoned"):
                reasoned[r["year"]] += 1

    docs = collections.defaultdict(
        lambda: {"court": collections.Counter(),
                 "party": collections.Counter(),
                 "carts": set(), "parts": set(), "y": 0})
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
                d["court"][r["t"]] += 1
                if a:
                    d["carts"].add(a)
            elif r["role"] in ("party_argument", "recital"):
                d["party"][r["t"]] += 1
                if a:
                    d["parts"].add(a)

    view = {"composition": {}, "authority": {}, "core": {}, "divergence": {},
            "functionMix": {}}
    for y in YEARS:
        n, rn = total[y], reasoned[y]
        view["composition"][str(y)] = {
            "judgments": n, "reasoned": rn,
            "reasonedSharePct": round(100 * rn / n, 1) if n else None}
        live = [d for d in docs.values() if d["y"] == y]
        if not rn or not live:
            continue
        fq = sum(d["court"]["fiqh_source"] for d in live)
        st = sum(d["court"]["statute"] for d in live)
        ns = sum(sum(d["court"][t] for t in NONSTATUTE) for d in live)
        dj = sum(1 for d in live if d["court"]["fiqh_source"])
        ds = sum(1 for d in live if d["court"]["statute"])
        hy = sum(1 for d in live if d["court"]["statute"]
                 and any(d["court"][t] for t in NONSTATUTE))
        view["authority"][str(y)] = {
            "fiqhPrevalenceReasonedPct": round(100 * dj / rn, 1),
            "fiqhPrevalenceCI": wilson(dj, rn),
            "fiqhPer1000Reasoned": round(1000 * fq / rn, 1),
            "statutePrevalenceReasonedPct": round(100 * ds / rn, 1),
            "statutePer1000Reasoned": round(1000 * st / rn, 1),
            "fiqhPerStatutoryCitation": round(fq / st, 3) if st else None,
            "nonStatutePerStatutoryCitation": round(ns / st, 3) if st else None,
            "hybridPrevalenceReasonedPct": round(100 * hy / rn, 1)}

    recent = [d for d in docs.values() if d["y"] in RECENT]
    c3 = collections.Counter()
    for d in recent:
        for a in d["carts"]:
            c3[a] += 1
    ranked = sorted(c3.items(), key=lambda kv: (-kv[1], kv[0]))
    view["core"] = {
        "window": sorted(RECENT),
        "distinctArticles": len(c3),
        "top50": [{"rank": i + 1, "article": f"{a[0]}:{a[1]}",
                   "judgments": v} for i, (a, v) in enumerate(ranked[:50])]}

    cf = collections.Counter()
    pf = collections.Counter()
    both = shared_inst = shared_art = 0
    for d in recent:
        for a in d["carts"]:
            lab = fn.get(f"{a[0]}:{a[1]}")
            cf[lab["function"] if lab else "unlabelled"] += 1
        for a in d["parts"]:
            lab = fn.get(f"{a[0]}:{a[1]}")
            pf[lab["function"] if lab else "unlabelled"] += 1
        if d["carts"] and d["parts"]:
            both += 1
            if {x[0] for x in d["carts"]} & {x[0] for x in d["parts"]}:
                shared_inst += 1
            if d["carts"] & d["parts"]:
                shared_art += 1
    tc, tp = sum(cf.values()), sum(pf.values())
    view["functionMix"] = {
        "court": {k: round(100 * v / tc, 1) for k, v in cf.most_common()},
        "party_wide": {k: round(100 * v / tp, 1) for k, v in pf.most_common()}}
    view["divergence"] = {
        "judgmentsWhereBothCiteStatute": both,
        "sharedInstrumentPct": round(100 * shared_inst / both, 1) if both else None,
        "sharedArticlePct": round(100 * shared_art / both, 1) if both else None}
    return view


def delta(old, new):
    print("COMPOSITION FIRST --- every other delta is conditional on it\n")
    for y in YEARS:
        a = old["composition"].get(str(y), {})
        b = new["composition"].get(str(y), {})
        if not b:
            continue
        print(f"  {y}  judgments {a.get('judgments','-'):>7} -> "
              f"{b['judgments']:>7}   reasoned share "
              f"{a.get('reasonedSharePct','-')} -> {b['reasonedSharePct']} %")
    print("\nAUTHORITY MIX, court voice, per reasoned judgment")
    keys = ("fiqhPrevalenceReasonedPct", "fiqhPer1000Reasoned",
            "statutePrevalenceReasonedPct", "statutePer1000Reasoned",
            "fiqhPerStatutoryCitation", "hybridPrevalenceReasonedPct")
    for y in YEARS:
        a, b = old["authority"].get(str(y)), new["authority"].get(str(y))
        if not b:
            continue
        moved = [f"{k} {a[k]} -> {b[k]}" for k in keys
                 if a and a.get(k) != b.get(k)]
        if moved:
            print(f"  {y}: " + "; ".join(moved))
    oldrank = {r["article"]: r["rank"] for r in old["core"]["top50"]}
    print("\nOPERATIONAL CORE")
    for r in new["core"]["top50"]:
        was = oldrank.get(r["article"])
        if was is None:
            print(f"  NEW at {r['rank']:>3}: {r['article']} "
                  f"({r['judgments']:,} judgments)")
        elif abs(was - r["rank"]) >= 3:
            print(f"  {r['article']}: {was} -> {r['rank']}")
    gone = set(oldrank) - {r["article"] for r in new["core"]["top50"]}
    for g in sorted(gone):
        print(f"  LEFT the top 50: {g} (was {oldrank[g]})")
    print("\nFUNCTION MIX AND SPEAKER DIVERGENCE")
    for voice in ("court", "party_wide"):
        for k, v in new["functionMix"][voice].items():
            o = old["functionMix"][voice].get(k)
            if o != v:
                print(f"  {voice} {k}: {o} -> {v} %")
    for k, v in new["divergence"].items():
        o = old["divergence"].get(k)
        if o != v:
            print(f"  {k}: {o} -> {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", help="an earlier monitor_view.json")
    args = ap.parse_args()
    view = build()
    if args.delta:
        delta(json.loads(Path(args.delta).read_text(encoding="utf-8")), view)
        return
    OUT.write_text(json.dumps(view, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{'year':<6}{'judg':>8}{'reasoned':>10}{'share':>8}"
          f"{'fiqh prev':>11}{'fiqh/1k':>9}{'statute prev':>14}"
          f"{'statute/1k':>12}{'fiqh/statute':>14}{'hybrid':>8}")
    for y in YEARS:
        c = view["composition"][str(y)]
        a = view["authority"].get(str(y))
        if not a:
            continue
        print(f"{y:<6}{c['judgments']:>8,}{c['reasoned']:>10,}"
              f"{c['reasonedSharePct']:>7.1f}%{a['fiqhPrevalenceReasonedPct']:>10.1f}%"
              f"{a['fiqhPer1000Reasoned']:>9.1f}"
              f"{a['statutePrevalenceReasonedPct']:>13.1f}%"
              f"{a['statutePer1000Reasoned']:>12.1f}"
              f"{a['fiqhPerStatutoryCitation']:>14.3f}"
              f"{a['hybridPrevalenceReasonedPct']:>7.1f}%")
    print(f"\ncourt function mix     {view['functionMix']['court']}")
    print(f"party (wide) mix       {view['functionMix']['party_wide']}")
    print(f"divergence             {view['divergence']}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
