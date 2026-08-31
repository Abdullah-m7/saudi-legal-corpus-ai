#!/usr/bin/env python3
"""Two statutory layers, or one?

The completeness theory died inside the statute books (see THEORY_LOG.md).
What survived its wreckage was an observation about the comparator rather than
the variable: institutional articles were the quiet ones. This tests that
directly, as a partition of the same 126 articles on a different question --
does this provision RUN THE ADJUDICATIVE PROCESS or HELP RESOLVE THE DISPUTE?

Everything is reported twice. Once on the hand labels, which were NOT made
blind: by the time they were assigned the annotator had seen supplementation
rates for most of these articles. And once on `ruleLabel`, a mechanical map
from the thirteen functions of `function.py`, which were assigned from enacted
text in an earlier session before any rate had been computed. Where the rule
map can place an article at all the two agree on 79.5 per cent of them, and if
the theory only holds on the contaminated labels it does not hold.

Sections, in the order the questions were asked:

    byClass          supplementation by functional class, two denominators
    withinInstrument the test the previous theory failed
    coreAnatomy      what the operational core is made of
    courtVsParty     does each voice carry a different layer of the statute
    transitions      same instrument, different article: different function?
    confusion        against procedural/substantive, and against completeness
    explanatory      which classification actually explains the variance

    python3 twolayers.py
"""
import collections
import gzip
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                        # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
GOLD = HERE / "adjudicative_function_gold.json"
COMP = HERE / "completeness_gold.json"
CORE = HERE / "core_view.json"
OUT = HERE / "twolayers_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
CLASSES = ["INSTITUTIONAL_OPERATION", "DISPUTE_DECISION", "MIXED", "AMBIGUOUS"]
KINDS = {"named_fiqh": ("fiqh_source",), "maxim": ("legal_maxim",),
         "scripture": ("quran", "hadith"),
         "judicial_principle": ("judicial_principle",),
         "custom": ("custom",)}


def key(k):
    a, b = k.rsplit(":", 1)
    return (a, int(b))


def scan():
    """One pass. judgment -> per-voice (types, articles, procedural flags)."""
    docs = collections.defaultdict(
        lambda: {"court": [collections.Counter(), set()],
                 "party": [collections.Counter(), set()],
                 "wide": [collections.Counter(), set()],
                 "y": 0})
    proc = {}
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            voices = []
            if r["role"] == "court_reasoning":
                voices = ["court"]
            elif r["role"] == "party_argument":
                voices = ["party", "wide"]
            elif r["role"] == "recital":
                voices = ["wide"]
            a = ((r["inst"], r["art"]) if r.get("inst")
                 and r.get("art") is not None else None)
            for v in voices:
                d[v][0][r["t"]] += 1
                if a:
                    d[v][1].add(a)
            if a is not None and "proc" in r:
                proc.setdefault(a, collections.Counter())[r["proc"]] += 1
    return docs, proc


def per_article(docs, voice, keys, years=None):
    n = collections.Counter()
    hit = collections.Counter()
    typed = collections.defaultdict(collections.Counter)
    shape = collections.defaultdict(collections.Counter)
    for d in docs.values():
        if years and d["y"] not in years:
            continue
        types, arts = d[voice]
        if not types:
            continue
        mixed = any(types[t] for t in NONSTATUTE)
        st = types["statute"] > 0
        sh = ("hybrid" if st and mixed else "statute_only" if st
              else "nonstatute_only" if mixed else "none")
        for a in arts & keys:
            n[a] += 1
            shape[a][sh] += 1
            if mixed:
                hit[a] += 1
            for name, ts in KINDS.items():
                if any(types[t] for t in ts):
                    typed[a][name] += 1
    return n, hit, typed, shape


def band(rows):
    if not rows:
        return None
    tot = sum(r[1] for r in rows)
    got = sum(r[2] for r in rows)
    rates = sorted(100 * r[2] / r[1] for r in rows)
    q = statistics.quantiles(rates, n=4) if len(rates) >= 4 else [None] * 3
    return {"articles": len(rows), "judgments": tot,
            "pooledPct": round(100 * got / tot, 1) if tot else None,
            "pooledCI": wilson(got, tot),
            "medianPct": round(statistics.median(rates), 1),
            "p25": round(q[0], 1) if q[0] is not None else None,
            "p75": round(q[2], 1) if q[2] is not None else None}


def by_class(labels, field, n, hit, keys):
    out = {}
    for cls in CLASSES:
        rows = [(k, n[k], hit[k]) for k in keys
                if labels[f"{k[0]}:{k[1]}"][field] == cls and n[k]]
        b = band(rows)
        if b:
            out[cls] = b
    return out


def main():
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    labels = gold["labels"]
    keys = {key(k) for k in labels}
    docs, proc = scan()
    n, hit, typed, shape = per_article(docs, "court", keys)

    res = {"nArticles": len(keys),
           "agreementWithRuleLabels": gold["agreementWithRuleLabels"],
           "byClass": by_class(labels, "function", n, hit, keys),
           "byClassRuleLabels": by_class(labels, "ruleLabel", n, hit, keys),
           "byClassUnambiguous": by_class(
               labels, "function", n, hit,
               {k for k in keys if not labels[f"{k[0]}:{k[1]}"]["ambiguous"]})}

    # reasoning shape and authority mix, per class
    mix = {}
    for cls in CLASSES:
        ks = [k for k in keys if labels[f"{k[0]}:{k[1]}"]["function"] == cls
              and n[k]]
        if not ks:
            continue
        tot = sum(n[k] for k in ks)
        row = {"judgments": tot}
        # only statute_only and hybrid can occur: the denominator is
        # judgments that cite this article, so a statute is present by
        # construction. The other two shapes are printed nowhere.
        for sh in ("statute_only", "hybrid"):
            row[sh] = round(100 * sum(shape[k][sh] for k in ks) / tot, 1)
        for name in KINDS:
            row[name] = round(100 * sum(typed[k][name] for k in ks) / tot, 1)
        mix[cls] = row
    res["shapeAndAuthorityByClass"] = mix

    # PHASE 5 --- within instrument, each shown separately
    inst = collections.defaultdict(set)
    for k in keys:
        inst[k[0]].add(k)
    within = {}
    for i, ks in sorted(inst.items()):
        rows = by_class(labels, "function", n, hit, ks)
        rule = by_class(labels, "ruleLabel", n, hit, ks)
        if len(rows) >= 2:
            within[i] = {"nArticles": len(ks), "hand": rows, "rule": rule}
    res["withinInstrument"] = within

    # PHASE 6 --- the functional anatomy of the operational core.
    # core_view.json stops at 50, and the question asks for 100, so the
    # ranking is recomputed here over contemporary_3y from the layer itself.
    c3 = collections.Counter()
    for d in docs.values():
        if d["y"] < 1444:
            continue
        for a in d["court"][1]:
            c3[a] += 1
    ranked = [a for a, _ in sorted(c3.items(), key=lambda kv: (-kv[1], kv[0]))]
    fn13 = json.loads(
        (HERE / "function_labels.json").read_text(encoding="utf-8"))["labels"]
    anat = {}
    for cut in (10, 25, 50, 100):
        top = ranked[:cut]
        tot = sum(c3[a] for a in top)
        c, sub, unlab = collections.Counter(), collections.Counter(), 0
        for a in top:
            lab = labels.get(f"{a[0]}:{a[1]}")
            if lab:
                c[lab["function"]] += c3[a]
                if lab["function"] == "INSTITUTIONAL_OPERATION":
                    f = (fn13.get(f"{a[0]}:{a[1]}") or {}).get("function",
                                                              "other")
                    sub[f] += c3[a]
            else:
                unlab += c3[a]
        anat[f"top{cut}"] = {
            "citingJudgments": tot,
            "unlabelledPct": round(100 * unlab / tot, 1),
            **{cls: round(100 * c[cls] / tot, 1) for cls in CLASSES},
            "institutionalSubtypesPctOfAll": {
                k: round(100 * v / tot, 1)
                for k, v in sub.most_common()},
        }
    res["coreAnatomy"] = anat
    res["coreAnatomyNote"] = (
        "citation-visible legal authority, not time spent and not importance. "
        "An article is counted once per judgment that cites it. The "
        "institutional subtypes come from function.py's thirteen functions, "
        "which are descriptive only and were never validated at function "
        "level; 'other' is where that classifier declined to place the "
        "article.")

    # PHASE 7 --- does each voice carry a different layer?
    cvp = {}
    for voice in ("court", "party", "wide"):
        vn, vh, _, _ = per_article(docs, voice, keys)
        tot = sum(vn.values())
        c = collections.Counter()
        for k in keys:
            c[labels[f"{k[0]}:{k[1]}"]["function"]] += vn[k]
        cvp[voice] = {"citationsToLabelledArticles": tot,
                      **{cls: round(100 * c[cls] / tot, 1) for cls in CLASSES}}
    res["courtVsParty"] = cvp

    # PHASE 8 --- same instrument, different article: different function?
    trans = {}
    for voice in ("party", "wide"):
        t = collections.Counter()
        docs_shared = 0
        for d in docs.values():
            if d["y"] < 1444:
                continue
            ca, pa = d["court"][1] & keys, d[voice][1] & keys
            if not ca or not pa:
                continue
            shared = {x[0] for x in ca} & {x[0] for x in pa}
            if not shared:
                continue
            docs_shared += 1
            for i in shared:
                cf = {labels[f"{x[0]}:{x[1]}"]["function"]
                      for x in ca if x[0] == i}
                pf = {labels[f"{x[0]}:{x[1]}"]["function"]
                      for x in pa if x[0] == i}
                same = {x for x in ca if x[0] == i} & {x for x in pa
                                                       if x[0] == i}
                for a in sorted(pf):
                    for b in sorted(cf):
                        t[(a, b, "same article present" if same
                           else "different articles")] += 1
        trans[voice] = {
            "judgmentsSharingAnInstrument": docs_shared,
            "table": {f"party={a} -> court={b} [{c}]": v
                      for (a, b, c), v in sorted(t.items(),
                                                 key=lambda kv: -kv[1])}}
    res["transitions"] = trans

    # PHASE 9 --- is this procedural/substantive under another name?
    ps = {}
    for k in keys:
        c = proc.get(k)
        if not c:
            continue
        ps[k] = "procedural" if c.get(1, 0) >= c.get(0, 0) else "substantive"
    conf = collections.Counter(
        (labels[f"{k[0]}:{k[1]}"]["function"], ps[k]) for k in ps)
    res["confusionWithProcedural"] = {
        "articlesWithAProceduralFlag": len(ps),
        "table": {f"{a} | {b}": c for (a, b), c in sorted(conf.items())}}
    conf2 = collections.Counter(
        (labels[f"{k[0]}:{k[1]}"]["function"],
         labels[f"{k[0]}:{k[1]}"]["completenessClass"]) for k in keys)
    res["confusionWithCompleteness"] = {
        f"{a} | {b}": c for (a, b), c in
        sorted(conf2.items(), key=lambda kv: (-kv[1], kv[0]))}

    # PHASE 10 --- which classification explains the article-level variance?
    rates = {k: 100 * hit[k] / n[k] for k in keys if n[k] >= 30}
    grand = statistics.mean(rates.values())
    tss = sum((v - grand) ** 2 for v in rates.values())

    def eta2(assign):
        groups = collections.defaultdict(list)
        for k, v in rates.items():
            groups[assign(k)].append(v)
        bss = sum(len(g) * (statistics.mean(g) - grand) ** 2
                  for g in groups.values())
        return round(bss / tss, 3), len(groups)

    def holdout(assign):
        """Fit group means on odd-ranked articles, score the even ones."""
        # ties in the citation count fall back to the article id: without
        # it the split depends on dict order and the reported MAE moves
        # between runs of the same code.
        ks = sorted(rates, key=lambda k: (-n[k], k))
        tr, te = ks[0::2], ks[1::2]
        g = collections.defaultdict(list)
        for k in tr:
            g[assign(k)].append(rates[k])
        base = statistics.mean(rates[k] for k in tr)
        err = [abs(rates[k] - (statistics.mean(g[assign(k)])
                               if g.get(assign(k)) else base)) for k in te]
        null = [abs(rates[k] - base) for k in te]
        return round(statistics.mean(err), 2), round(statistics.mean(null), 2)

    schemes = {
        "A_procedural_substantive": lambda k: ps.get(k, "unknown"),
        "B_completeness": lambda k: labels[f"{k[0]}:{k[1]}"]["completenessClass"],
        "C_institutional_dispute": lambda k: labels[f"{k[0]}:{k[1]}"]["function"],
        "C_rule_labels": lambda k: labels[f"{k[0]}:{k[1]}"]["ruleLabel"],
        "D_instrument": lambda k: k[0],
    }
    exp = {}
    for name, f in schemes.items():
        e, g = eta2(f)
        mae, null = holdout(f)
        exp[name] = {"groups": g, "etaSquared": e,
                     "holdoutMAE": mae, "holdoutMAEofGrandMean": null,
                     "improvementPts": round(null - mae, 2)}
    res["explanatoryPower"] = {
        "articles": len(rates),
        "note": "eta-squared is the share of between-article variance in the "
                "supplementation rate that the grouping accounts for, on "
                "articles with at least 30 court-citing judgments. The "
                "hold-out fits group means on every second article by "
                "citation rank and scores the rest, against the grand mean "
                "as the null. Neither is a causal claim.",
        **exp}

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    for title, k in (("hand labels", "byClass"),
                     ("rule labels (blind, earlier session)",
                      "byClassRuleLabels")):
        print(f"\n[{title}]  {'class':<26}{'arts':>5}{'judg':>8}"
              f"{'pooled':>9}{'median':>9}")
        for cls, b in res[k].items():
            print(f"{'':<14}{cls:<26}{b['articles']:>5}{b['judgments']:>8,}"
                  f"{b['pooledPct']:>8.1f}%{b['medianPct']:>8.1f}%")
    print("\nexplanatory power (article-level rate, n>=30):")
    for name, v in exp.items():
        print(f"  {name:<26}groups {v['groups']:>3}  eta2 {v['etaSquared']:>6}"
              f"  hold-out MAE {v['holdoutMAE']:>6} vs {v['holdoutMAEofGrandMean']}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
