#!/usr/bin/env python3
"""Does each modern Saudi code generate a characteristic supplementary
authority pattern?

"Authority ecology" is used here as an analytic label and nothing more: the
profile of what appears *beside* an instrument when a court cites it. The
question is whether the profile is a property of the code or of the corpus.
It is answered by building the same profile for every instrument with enough
observations and putting them side by side; no clustering, because with eight
instruments a table is clearer than a dendrogram.

Two instruments get an article-level dive, because they are the two recent
substantive codes and they organise different work: the Evidence Law
(1443) allocates proof, the Civil Transactions Law (1444) creates
entitlements.

Non-citation is not non-application. An article of the Civil Transactions Law
that no published commercial judgment cites may govern transactions that never
reach a commercial court, or be so clear that nobody litigates it. What is
measured is adjudicatory visibility in published commercial judgments.

    python3 ecology.py
"""
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
FUNC = HERE / "adjudicative_function_gold.json"
OUT = HERE / "ecology_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
KINDS = {"named_fiqh": ("fiqh_source",), "maxim": ("legal_maxim",),
         "scripture": ("quran", "hadith"),
         "judicial_principle": ("judicial_principle",),
         "custom": ("custom",)}
YEARS3 = {1444, 1445, 1446}
POST_CTL = {1445, 1446}


def scan():
    docs = collections.defaultdict(
        lambda: {"court": [collections.Counter(), set()],
                 "wide": [collections.Counter(), set()],
                 "strict": [collections.Counter(), set()], "y": 0})
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            vs = ({"court"} if r["role"] == "court_reasoning" else
                  {"strict", "wide"} if r["role"] == "party_argument" else
                  {"wide"} if r["role"] == "recital" else set())
            a = ((r["inst"], r["art"]) if r.get("inst")
                 and r.get("art") is not None else None)
            for v in vs:
                d[v][0][r["t"]] += 1
                if a:
                    d[v][1].add(a)
    return docs


def profile(docs, instrument, years):
    """One instrument's ecology: what appears beside it when a court cites it."""
    n = tot = 0
    kinds = collections.Counter()
    arts = collections.Counter()
    party = collections.Counter()
    both = shared_art = 0
    for d in docs.values():
        if d["y"] not in years:
            continue
        ca = {a for a in d["court"][1] if a[0] == instrument}
        pa = {a for a in d["wide"][1] if a[0] == instrument}
        for a in pa:
            party[a] += 1
        if not ca:
            continue
        n += 1
        for a in ca:
            arts[a] += 1
        types = d["court"][0]
        if any(types[t] for t in NONSTATUTE):
            tot += 1
        for name, ts in KINDS.items():
            if any(types[t] for t in ts):
                kinds[name] += 1
        if pa:
            both += 1
            if ca & pa:
                shared_art += 1
    if not n:
        return None
    top = arts.most_common(10)
    cum = sum(v for _, v in top)
    return {
        "courtCitingJudgments": n,
        "distinctArticlesCourt": len(arts),
        "distinctArticlesParty": len(party),
        "hybridPct": round(100 * tot / n, 1),
        "hybridCI": wilson(tot, n),
        "statuteOnlyPct": round(100 * (n - tot) / n, 1),
        **{k: round(100 * kinds[k] / n, 1) for k in KINDS},
        "top10ShareOfCitations": round(100 * cum / sum(arts.values()), 1),
        "topArticles": [{"article": a[1], "judgments": v} for a, v in top],
        "judgmentsWhereBothSidesCiteIt": both,
        "sameArticlePctWhenBoth":
            round(100 * shared_art / both, 1) if both else None,
    }


def dive(docs, instrument, years, minimum):
    fn = json.loads(FUNC.read_text(encoding="utf-8"))["labels"]
    cn = collections.Counter()
    hit = collections.Counter()
    typed = collections.defaultdict(collections.Counter)
    pn = collections.Counter()
    shared = collections.Counter()
    for d in docs.values():
        if d["y"] not in years:
            continue
        ca = {a for a in d["court"][1] if a[0] == instrument}
        pa = {a for a in d["wide"][1] if a[0] == instrument}
        types = d["court"][0]
        mixed = any(types[t] for t in NONSTATUTE)
        for a in pa:
            pn[a] += 1
        for a in ca:
            cn[a] += 1
            if mixed:
                hit[a] += 1
            for name, ts in KINDS.items():
                if any(types[t] for t in ts):
                    typed[a][name] += 1
            if a in pa:
                shared[a] += 1
    rows = []
    for a in sorted(set(cn) | set(pn), key=lambda a: -(cn[a] + pn[a])):
        if cn[a] < minimum and pn[a] < minimum:
            continue
        rows.append({
            "article": a[1],
            "courtJudgments": cn[a], "partyJudgments": pn[a],
            "bothPct": round(100 * shared[a] / cn[a], 1) if cn[a] else None,
            "hybridPct": round(100 * hit[a] / cn[a], 1) if cn[a] else None,
            **{k: (round(100 * typed[a][k] / cn[a], 1) if cn[a] else None)
               for k in KINDS},
            "function": (fn.get(f"{instrument}:{a[1]}") or {}).get("function"),
        })
    return {"instrument": instrument, "years": sorted(years),
            "minJudgments": minimum,
            "courtOnly": sum(1 for r in rows if r["courtJudgments"]
                             and not r["partyJudgments"]),
            "partyOnly": sum(1 for r in rows if r["partyJudgments"]
                             and not r["courtJudgments"]),
            "articles": rows}


def main():
    docs = scan()
    insts = collections.Counter()
    for d in docs.values():
        if d["y"] in YEARS3:
            for a in d["court"][1]:
                insts[a[0]] += 1
    res = {"window": sorted(YEARS3), "profiles": {}, "dives": {}}
    for i, c in insts.most_common():
        if c < 100:
            continue
        p = profile(docs, i, YEARS3)
        if p:
            res["profiles"][i] = p
    res["dives"]["civil_transactions_law"] = dive(
        docs, "civil_transactions_law", POST_CTL, 8)
    res["dives"]["evidence_law"] = dive(docs, "evidence_law", POST_CTL, 25)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    w = 42
    print(f"{'instrument':<{w}}{'judg':>7}{'hybrid':>8}{'fiqh':>7}{'maxim':>7}"
          f"{'script':>8}{'judprin':>9}{'custom':>8}{'top10share':>12}")
    for i, p in res["profiles"].items():
        print(f"  {i[:w-2]:<{w-2}}{p['courtCitingJudgments']:>7,}"
              f"{p['hybridPct']:>7.1f}%{p['named_fiqh']:>6.1f}%"
              f"{p['maxim']:>6.1f}%{p['scripture']:>7.1f}%"
              f"{p['judicial_principle']:>8.1f}%{p['custom']:>7.1f}%"
              f"{p['top10ShareOfCitations']:>11.1f}%")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
