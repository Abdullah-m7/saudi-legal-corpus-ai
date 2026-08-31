#!/usr/bin/env python3
"""How much of the instrument effect survives the articles inside it?

`instrument_effect.py` ruled out three explanations for why statute books
differ -- citation load, crude case mix, and the code's own textual features.
It left the decisive question open, because it worked at the level of the
code. Three quarters of the variance in supplementation is *inside* codes, and
a code is nothing but its articles. So the instrument effect could be entirely
a mix effect: the Arbitration Law may simply contain the kinds of article that
are never supplemented, and the Law of Practice the kinds that always are.

Two tests, both at the article level.

    SEQUENTIAL. Fit the article's own properties first -- what it does, how
    long it is, how much it is cited, what vocabulary it uses -- and then ask
    what instrument identity adds. Then reverse the order. If instrument adds
    nothing over article properties, the ecology was the article mix.

    FUNCTION-MATCHED PAIRS. Take two articles doing the same adjudicative
    work, cited about equally often, in different codes, and compare them
    directly. This is the cleanest form of the question: a jurisdiction
    article in one book against a jurisdiction article in another.

Everything is descriptive. With 133 measurable articles across twelve codes,
a fitted model would be arithmetic dressed as inference, so the measures are
variance shares and hold-out error against an explicit null.

    python3 article_instrument.py
"""
import collections
import gzip
import itertools
import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from function import articles, MARKS          # noqa: E402
from map import wilson                        # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
FUNC = HERE / "adjudicative_function_gold.json"
INST = HERE / "instruments_results.json"
OUT = HERE / "article_instrument_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
RECENT = {1444, 1445, 1446}
MIN = 30

XREF = re.compile(r"المادة\s*\(|المادتين|المواد\s*\(|من النظام|من اللائحة")
SHARIA = re.compile(r"الشريعة|أحكام الشرع|الفقه|شرعا|شرعي")
CUSTOM = re.compile(r"العرف|العادة المستقرة|المتعارف")
DISCR = re.compile(r"يجوز|للمحكمة أن|فللمحكمة|ما تراه|تقدير|السلطة التقديرية")
OPEN = re.compile(r"مناسب|ملائم|معقول|جسامة|عذر|مسوغ|ضرورة|الحاجة|"
                  r"عند الاقتضاء|بحسب الأحوال|جوهري|كافي|كافية|الظاهر")


def scan():
    docs = collections.defaultdict(
        lambda: {"c": collections.Counter(), "ca": set(), "pw": set(),
                 "pc": collections.Counter(), "y": 0})
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
            elif r["role"] in ("party_argument", "recital"):
                d["pc"][r["t"]] += 1
                if a:
                    d["pw"].add(a)
    return docs


def band(n):
    return 0 if n < 60 else 1 if n < 150 else 2 if n < 400 else 3


def main():
    docs = scan()
    A = articles()
    fn = json.loads(FUNC.read_text(encoding="utf-8"))["labels"]
    feats_by_inst = json.loads(INST.read_text(encoding="utf-8"))["features"]

    n = collections.Counter()
    hit = collections.Counter()
    yrs = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    pn = collections.Counter()
    ph = collections.Counter()
    for d in docs.values():
        mixed = any(d["c"][t] for t in NONSTATUTE)
        pmix = any(d["pc"][t] for t in NONSTATUTE)
        for a in d["ca"]:
            n[a] += 1
            if mixed:
                hit[a] += 1
            y = yrs[a][d["y"]]
            y[0] += 1
            y[1] += mixed
        for a in d["pw"]:
            pn[a] += 1
            if pmix:
                ph[a] += 1

    rows = {}
    for a in n:
        if n[a] < MIN:
            continue
        rec = A.get(a)
        t = MARKS.sub("", rec["text"]) if rec else ""
        lab = fn.get(f"{a[0]}:{a[1]}") or {}
        f = feats_by_inst.get(a[0], {})
        rows[a] = {
            "rate": 100 * hit[a] / n[a],
            "instrument": a[0],
            "citations": n[a],
            "citationBand": band(n[a]),
            "function": lab.get("function", "unlabelled"),
            "words": len(t.split()) if t else None,
            "xref": len(XREF.findall(t)) if t else None,
            "sharia": bool(SHARIA.search(t)) if t else None,
            "custom": bool(CUSTOM.search(t)) if t else None,
            "discretionary": bool(DISCR.search(t)) if t else None,
            "openTextured": bool(OPEN.search(t)) if t else None,
            "yearsObserved": f.get("yearsObservedTo1446"),
            "partyCitations": pn[a],
        }
    have = {a: r for a, r in rows.items() if r["words"] is not None}
    grand = statistics.mean(r["rate"] for r in rows.values())
    tss = sum((r["rate"] - grand) ** 2 for r in rows.values())

    def share(keyf, source=rows):
        g = collections.defaultdict(list)
        for a, r in source.items():
            g[keyf(a, r)].append(r["rate"])
        gm = statistics.mean(r["rate"] for r in source.values())
        t = sum((r["rate"] - gm) ** 2 for r in source.values())
        b = sum(len(v) * (statistics.mean(v) - gm) ** 2 for v in g.values())
        return round(100 * b / t, 1), len(g)

    # SEQUENTIAL: residualise on one scheme, then measure what the other
    # explains of what is left. Order matters, so both orders are reported.
    def residuals(keyf, source):
        g = collections.defaultdict(list)
        for a, r in source.items():
            g[keyf(a, r)].append(r["rate"])
        mean = {k: statistics.mean(v) for k, v in g.items()}
        return {a: r["rate"] - mean[keyf(a, r)] for a, r in source.items()}

    def share_of(res, keyf, source):
        g = collections.defaultdict(list)
        for a, v in res.items():
            g[keyf(a, source[a])].append(v)
        gm = statistics.mean(res.values())
        t = sum((v - gm) ** 2 for v in res.values())
        b = sum(len(v) * (statistics.mean(v) - gm) ** 2 for v in g.values())
        return round(100 * b / t, 1) if t else 0.0

    ARTICLE_KEY = lambda a, r: (          # noqa: E731
        r["function"], r["citationBand"], bool(r["openTextured"]),
        (r["words"] or 0) >= 40)
    INST_KEY = lambda a, r: r["instrument"]   # noqa: E731

    seq = {
        "articlePropertiesFirst": {
            "articleShare": share(ARTICLE_KEY, have)[0],
            "instrumentShareOfResidual": share_of(
                residuals(ARTICLE_KEY, have), INST_KEY, have)},
        "instrumentFirst": {
            "instrumentShare": share(INST_KEY, have)[0],
            "articleShareOfResidual": share_of(
                residuals(INST_KEY, have), ARTICLE_KEY, have)},
        "note": "article properties are the adjudicative function, the "
                "citation band, whether the article's own text carries "
                "open-textured vocabulary, and whether it is longer than the "
                "corpus median. Groups are cells of that cross, so the share "
                "is inflated by cell count and is comparable between the two "
                "orders, not against zero.",
        "articles": len(have),
        "articleCells": share(ARTICLE_KEY, have)[1],
        "instrumentGroups": share(INST_KEY, have)[1],
    }

    # A grouping with more cells explains more by chance alone, and the
    # article scheme has 34 cells against the instrument's 8. So every share
    # is reported beside the share the SAME cell sizes achieve on shuffled
    # rates: the excess is what the grouping actually carries.
    import random

    def chance(keyf, source, reps=400, seed=11):
        sizes = collections.Counter(keyf(a, r) for a, r in source.items())
        vals = [r["rate"] for r in source.values()]
        gm = statistics.mean(vals)
        t = sum((v - gm) ** 2 for v in vals)
        rng = random.Random(seed)
        out = []
        for _ in range(reps):
            rng.shuffle(vals)
            i, b = 0, 0.0
            for k, m in sizes.items():
                g = vals[i:i + m]
                i += m
                b += m * (statistics.mean(g) - gm) ** 2
            out.append(100 * b / t)
        return round(statistics.mean(out), 1)

    seq["chanceShares"] = {
        "articleProperties": chance(ARTICLE_KEY, have),
        "instrument": chance(INST_KEY, have),
        "note": "mean between-share achieved by the same cell sizes on "
                "shuffled article rates, over 400 shuffles. Subtract it from "
                "the observed share to compare schemes of different size.",
    }

    # PHASE 16 --- the full ranking, on one common denominator.
    ranking = {}
    for label, keyf in (
            ("instrument", lambda a, r: r["instrument"]),
            ("adjudicative function", lambda a, r: r["function"]),
            ("citation band", lambda a, r: r["citationBand"]),
            ("open-textured vocabulary", lambda a, r: bool(r["openTextured"])),
            ("article longer than median", lambda a, r: (r["words"] or 0) >= 40),
            ("years since commencement", lambda a, r: r["yearsObserved"]),
            ("has a party citation at all", lambda a, r: r["partyCitations"] > 0)):
        s, g = share(keyf, have)
        c = chance(keyf, have)
        ranking[label] = {"groups": g, "betweenSharePct": s,
                          "chanceSharePct": c,
                          "excessPts": round(s - c, 1)}
    # year is a property of the judgment, not the article, so it gets its own
    # denominator: the same articles, split by year.
    ycells = {}
    for a, per in yrs.items():
        if a not in rows:
            continue
        for y, (tot, k) in per.items():
            if tot >= 20:
                ycells[(a, y)] = 100 * k / tot
    gm = statistics.mean(ycells.values())
    tt = sum((v - gm) ** 2 for v in ycells.values())
    gy = collections.defaultdict(list)
    gi = collections.defaultdict(list)
    for (a, y), v in ycells.items():
        gy[y].append(v)
        gi[a[0]].append(v)
    ranking["year (article-year cells)"] = {
        "chanceSharePct": None, "excessPts": None,
        "groups": len(gy),
        "betweenSharePct": round(100 * sum(
            len(v) * (statistics.mean(v) - gm) ** 2 for v in gy.values()) / tt, 1)}
    ranking["instrument (same article-year cells)"] = {
        "chanceSharePct": None, "excessPts": None,
        "groups": len(gi),
        "betweenSharePct": round(100 * sum(
            len(v) * (statistics.mean(v) - gm) ** 2 for v in gi.values()) / tt, 1)}

    # FUNCTION-MATCHED CROSS-CODE PAIRS
    pairs = []
    keys = [a for a, r in rows.items() if r["function"] in
            ("INSTITUTIONAL_OPERATION", "DISPUTE_DECISION", "MIXED")]
    for a, b in itertools.combinations(sorted(keys), 2):
        ra, rb = rows[a], rows[b]
        if ra["instrument"] == rb["instrument"]:
            continue
        if ra["function"] != rb["function"]:
            continue
        if ra["citationBand"] != rb["citationBand"]:
            continue
        pairs.append({
            "function": ra["function"],
            "band": ra["citationBand"],
            "a": f"{a[0]}:{a[1]}", "aN": ra["citations"],
            "aPct": round(ra["rate"], 1),
            "b": f"{b[0]}:{b[1]}", "bN": rb["citations"],
            "bPct": round(rb["rate"], 1),
            "absGapPts": round(abs(ra["rate"] - rb["rate"]), 1)})
    same_inst = []
    for a, b in itertools.combinations(sorted(keys), 2):
        ra, rb = rows[a], rows[b]
        if ra["instrument"] != rb["instrument"]:
            continue
        if ra["function"] != rb["function"] or ra["citationBand"] != rb["citationBand"]:
            continue
        same_inst.append(abs(ra["rate"] - rb["rate"]))
    gaps = [p["absGapPts"] for p in pairs]
    matched = {
        "note": "pairs of articles doing the same adjudicative work, in the "
                "same citation band, in DIFFERENT codes -- and, as the "
                "control, the same construction inside ONE code. If the code "
                "carries something, the cross-code gap should be the larger.",
        "crossCodePairs": len(pairs),
        "crossCodeMedianGapPts": round(statistics.median(gaps), 1) if gaps else None,
        "crossCodeMeanGapPts": round(statistics.mean(gaps), 1) if gaps else None,
        "sameCodePairs": len(same_inst),
        "sameCodeMedianGapPts": round(statistics.median(same_inst), 1)
        if same_inst else None,
        "sameCodeMeanGapPts": round(statistics.mean(same_inst), 1)
        if same_inst else None,
        "byFunction": {},
        "widest": sorted(pairs, key=lambda p: -p["absGapPts"])[:8],
        "narrowest": sorted(pairs, key=lambda p: p["absGapPts"])[:5],
    }
    for f in ("INSTITUTIONAL_OPERATION", "DISPUTE_DECISION", "MIXED"):
        g = [p["absGapPts"] for p in pairs if p["function"] == f]
        s = [abs(rows[a]["rate"] - rows[b]["rate"])
             for a, b in itertools.combinations(sorted(keys), 2)
             if rows[a]["instrument"] == rows[b]["instrument"]
             and rows[a]["function"] == f == rows[b]["function"]
             and rows[a]["citationBand"] == rows[b]["citationBand"]]
        if g:
            matched["byFunction"][f] = {
                "crossCodePairs": len(g),
                "crossCodeMedianGapPts": round(statistics.median(g), 1),
                "sameCodePairs": len(s),
                "sameCodeMedianGapPts": round(statistics.median(s), 1) if s else None}

    res = {"window": "contemporary_5y, articles cited in >= 30 judgments",
           "articles": len(rows),
           "articlesWithText": len(have),
           "grandMeanPct": round(grand, 1),
           "sequential": seq,
           "varianceRanking": dict(sorted(
               ranking.items(),
               key=lambda kv: -(kv[1].get("excessPts")
                                if kv[1].get("excessPts") is not None
                                else kv[1]["betweenSharePct"]))),
           "functionMatchedPairs": matched}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print(f"{len(rows)} articles, {len(have)} with enacted text; "
          f"grand mean {grand:.1f} %\n")
    c = seq["chanceShares"]
    print(f"chance share for a grouping of this size: article properties "
          f"{c['articleProperties']} %, instrument {c['instrument']} %\n")
    print("SEQUENTIAL --- what does each add over the other?")
    s = seq["articlePropertiesFirst"]
    print(f"  article properties first ({seq['articleCells']} cells): "
          f"{s['articleShare']} %   then instrument adds "
          f"{s['instrumentShareOfResidual']} % of what is left")
    s = seq["instrumentFirst"]
    print(f"  instrument first ({seq['instrumentGroups']} codes):        "
          f"{s['instrumentShare']} %   then article properties add "
          f"{s['articleShareOfResidual']} % of what is left")
    print("\nVARIANCE RANKING --- share of between-article variance explained")
    for k, v in res["varianceRanking"].items():
        e = v.get("excessPts")
        print(f"  {k:<38}{v['groups']:>3} groups{v['betweenSharePct']:>8.1f} %"
              + (f"   chance {v['chanceSharePct']:>4.1f}   excess "
                 f"{e:>+5.1f}" if e is not None else ""))
    m = matched
    print(f"\nFUNCTION-MATCHED PAIRS")
    print(f"  across codes: {m['crossCodePairs']:,} pairs, median gap "
          f"{m['crossCodeMedianGapPts']} pts")
    print(f"  inside one code: {m['sameCodePairs']:,} pairs, median gap "
          f"{m['sameCodeMedianGapPts']} pts")
    for f, v in m["byFunction"].items():
        print(f"    {f:<26}cross {v['crossCodeMedianGapPts']:>5} "
              f"(n={v['crossCodePairs']:,})   same {v['sameCodeMedianGapPts']} "
              f"(n={v['sameCodePairs']})")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
