#!/usr/bin/env python3
"""Does the text of a provision predict when the bench reasons past it?

The seam finding was that the bench's reach outside the statute book varies
by article from 1.1 to 85.9 per cent, and that the structural/dispute-specific
distinction explains three points of that eighty. The obvious next hypothesis
is that what varies is the *completeness* of the provision: an article that
decides its point by itself needs nothing added, an article that hands the
judge a standard without its content does.

Stating that carefully is the whole difficulty, because the tempting version
is circular -- call an article incomplete because it attracts fiqh, then
report that incomplete articles attract fiqh. So the classification is made
FIRST, from the enacted text alone, blind to every rate, and frozen in
`completeness_gold.json` before this script is written. This script only
joins that frozen classification to the judgments.

Six classes, in priority order: EXTERNAL_REFERRAL, OPEN_TEXTURED_STANDARD,
DUTY_OR_POWER_WITHOUT_DECISION_RULE, DEFINITION_STATUS,
INSTITUTIONAL_DIRECTIVE, SELF_SUFFICIENT_RULE.

Two denominators are reported for every comparison, because they answer
different questions and can disagree:

    judgment-level   pool every judgment citing an article of the class.
                     Weighted by citation frequency, so art. 16 dominates.
    article-level    one observation per article, then the median. Unweighted,
                     so a rule about provisions is not a rule about art. 16.

    python3 completeness.py
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
from map import wilson                       # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
GOLD = HERE / "completeness_gold.json"
OUT = HERE / "completeness_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
ORDER = ["EXTERNAL_REFERRAL", "OPEN_TEXTURED_STANDARD",
         "DUTY_OR_POWER_WITHOUT_DECISION_RULE", "DEFINITION_STATUS",
         "INSTITUTIONAL_DIRECTIVE", "SELF_SUFFICIENT_RULE"]


def judgments(role):
    """judgment -> (articles cited in `role`, authority types in `role`)."""
    out = collections.defaultdict(
        lambda: [set(), collections.Counter()])
    roles = {"court": {"court_reasoning"},
             "party": {"party_argument"},
             "party_wide": {"party_argument", "recital"}}[role]
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["role"] not in roles:
                continue
            d = out[r["j"]]
            d[1][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[0].add((r["inst"], r["art"]))
    return out


def per_article(docs, keys):
    """For each article: judgments citing it, and how many are mixed."""
    n = collections.Counter()
    hit = collections.Counter()
    typed = collections.defaultdict(collections.Counter)
    for arts, types in docs.values():
        mixed = any(types[t] for t in NONSTATUTE)
        for a in arts & keys:
            n[a] += 1
            if mixed:
                hit[a] += 1
            for t in NONSTATUTE:
                if types[t]:
                    typed[a][t] += 1
    return n, hit, typed


def sign_test(k, n):
    """Two-sided exact binomial at p=0.5 --- no scipy in this environment."""
    if not n:
        return 1.0
    c = [1]
    for i in range(n):
        c = [1] + [c[j] + c[j + 1] for j in range(len(c) - 1)] + [1]
    tot = float(2 ** n)
    lo = min(k, n - k)
    tail = sum(c[i] for i in range(lo + 1)) / tot
    return min(1.0, 2 * tail)


def band(rows):
    """rows = [(k, n, hits)] -> the two denominators, side by side."""
    if not rows:
        return None
    tot = sum(r[1] for r in rows)
    got = sum(r[2] for r in rows)
    rates = sorted(100 * r[2] / r[1] for r in rows)
    q = statistics.quantiles(rates, n=4) if len(rates) >= 4 else [None] * 3
    return {
        "articles": len(rows),
        "judgments": tot,
        "judgmentLevelPct": round(100 * got / tot, 1) if tot else None,
        "judgmentLevelCI": wilson(got, tot),
        "articleMedianPct": round(statistics.median(rates), 1),
        "articleP25": round(q[0], 1) if q[0] is not None else None,
        "articleP75": round(q[2], 1) if q[2] is not None else None,
        "articleMinPct": round(rates[0], 1),
        "articleMaxPct": round(rates[-1], 1),
    }


def by_class(labels, n, hit, keys):
    out = {}
    for cls in ORDER:
        rows = [(k, n[k], hit[k]) for k in keys
                if labels[f"{k[0]}:{k[1]}"]["class"] == cls and n[k]]
        b = band(rows)
        if b:
            out[cls] = b
    return out


def main():
    gold = json.loads(GOLD.read_text(encoding="utf-8"))
    labels = gold["labels"]
    keys = {tuple([k.rsplit(":", 1)[0], int(k.rsplit(":", 1)[1])])
            for k in labels}
    keys = {(a, b) for a, b in keys}
    unseen = {k for k in keys
              if not labels[f"{k[0]}:{k[1]}"]["ratePreviouslySeen"]}
    unamb = {k for k in keys if not labels[f"{k[0]}:{k[1]}"]["ambiguous"]}

    court = judgments("court")
    n, hit, typed = per_article(court, keys)

    res = {
        "frame": gold["frame"],
        "nArticles": len(keys),
        "nJudgmentsWithCourtAuthority": len(court),
        "byClass": by_class(labels, n, hit, keys),
        "byClassUnseenOnly": by_class(labels, n, hit, unseen),
        "byClassUnambiguousOnly": by_class(labels, n, hit, unamb),
    }

    # PHASE 6 --- within instrument. The between-class difference could be a
    # difference between statute books; only a within-book comparison can say.
    inst = collections.defaultdict(set)
    for k in keys:
        inst[k[0]].add(k)
    within = {}
    for i, ks in sorted(inst.items()):
        rows = by_class(labels, n, hit, ks)
        if len(rows) >= 2:
            within[i] = {"nArticles": len(ks), "byClass": rows}
    res["withinInstrument"] = within

    # PHASE 9 --- which authority, not just whether.
    kinds = {"named_fiqh": ("fiqh_source",), "maxim": ("legal_maxim",),
             "scripture": ("quran", "hadith"),
             "judicial_principle": ("judicial_principle",),
             "custom": ("custom",)}
    bykind = {}
    for cls in ORDER:
        ks = [k for k in keys
              if labels[f"{k[0]}:{k[1]}"]["class"] == cls and n[k]]
        if not ks:
            continue
        tot = sum(n[k] for k in ks)
        bykind[cls] = {"judgments": tot}
        for name, ts in kinds.items():
            got = sum(sum(typed[k][t] for t in ts) for k in ks)
            bykind[cls][name] = round(100 * got / tot, 1) if tot else 0.0
    res["byClassByAuthority"] = bykind

    # PHASE 10 --- bench against bar, on the same articles.
    for spec in ("party", "party_wide"):
        docs = judgments(spec)
        pn, ph, _ = per_article(docs, keys)
        rows = []
        for k in sorted(keys):
            if n[k] >= 30 and pn[k] >= 30:
                c = 100 * hit[k] / n[k]
                p = 100 * ph[k] / pn[k]
                rows.append({"article": f"{k[0]}:{k[1]}",
                             "class": labels[f"{k[0]}:{k[1]}"]["class"],
                             "courtN": n[k], "courtPct": round(c, 1),
                             "partyN": pn[k], "partyPct": round(p, 1),
                             "deltaPts": round(c - p, 1)})
        rows.sort(key=lambda r: -r["deltaPts"])
        res[f"benchVsBar_{spec}"] = {
            "minN": 30, "nArticles": len(rows),
            "medianDeltaPts": round(
                statistics.median(r["deltaPts"] for r in rows), 1)
            if rows else None,
            "courtHigherOn": sum(1 for r in rows if r["deltaPts"] > 0),
            "byClass": {
                cls: round(statistics.median(
                    [r["deltaPts"] for r in rows if r["class"] == cls]), 1)
                for cls in ORDER
                if any(r["class"] == cls for r in rows)},
            "articles": rows,
        }

    # PHASE 7 --- matched pairs. Both the pooled and the median comparison
    # let one instrument, or one heavily cited article, carry the result.
    # Pairing inside an instrument and inside a citation band removes both,
    # at the cost of a small n. This is robustness, not identification: the
    # articles are not randomly assigned to their own texts.
    def bandof(x):
        return 0 if x < 60 else 1 if x < 150 else 2 if x < 400 else 3
    SUPP = {"OPEN_TEXTURED_STANDARD", "EXTERNAL_REFERRAL",
            "DUTY_OR_POWER_WITHOUT_DECISION_RULE"}
    pairs, used = [], set()
    for k in sorted(keys, key=lambda k: -n[k]):
        if not n[k] or k in used:
            continue
        if labels[f"{k[0]}:{k[1]}"]["class"] not in SUPP:
            continue
        cand = [m for m in keys
                if m not in used and n[m]
                and m[0] == k[0] and bandof(n[m]) == bandof(n[k])
                and labels[f"{m[0]}:{m[1]}"]["class"] not in SUPP]
        if not cand:
            continue
        m = min(cand, key=lambda m: abs(n[m] - n[k]))
        used |= {k, m}
        a, b = 100 * hit[k] / n[k], 100 * hit[m] / n[m]
        pairs.append({"instrument": k[0],
                      "supplementable": f"{k[0]}:{k[1]}",
                      "supplementableClass": labels[f"{k[0]}:{k[1]}"]["class"],
                      "supplementableN": n[k],
                      "supplementablePct": round(a, 1),
                      "complete": f"{m[0]}:{m[1]}",
                      "completeClass": labels[f"{m[0]}:{m[1]}"]["class"],
                      "completeN": n[m], "completePct": round(b, 1),
                      "deltaPts": round(a - b, 1)})
    pos = sum(1 for q in pairs if q["deltaPts"] > 0)
    neg = sum(1 for q in pairs if q["deltaPts"] < 0)
    res["matchedPairs"] = {
        "matchedOn": "instrument and citation band (<60, 60-149, 150-399, 400+)",
        "signTestP": round(sign_test(pos, pos + neg), 3),
        "n": len(pairs),
        "medianDeltaPts": round(
            statistics.median(p["deltaPts"] for p in pairs), 1)
        if pairs else None,
        "positive": sum(1 for p in pairs if p["deltaPts"] > 0),
        "pairs": pairs,
    }

    res["articles"] = [
        {"article": f"{k[0]}:{k[1]}",
         "class": labels[f"{k[0]}:{k[1]}"]["class"],
         "ambiguous": labels[f"{k[0]}:{k[1]}"]["ambiguous"],
         "fiqhIdiom": labels[f"{k[0]}:{k[1]}"]["fiqhIdiom"],
         "ratePreviouslySeen": labels[f"{k[0]}:{k[1]}"]["ratePreviouslySeen"],
         "judgments": n[k], "nonStatutePct": round(100 * hit[k] / n[k], 1)}
        for k in sorted(keys, key=lambda k: -n[k]) if n[k]]

    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    w = 36
    for title, key in (("all 126 articles", "byClass"),
                       ("unseen articles only", "byClassUnseenOnly")):
        print(f"\n[{title}]")
        print(f"{'class':<{w}}{'arts':>5}{'judg':>8}{'pooled':>9}"
              f"{'median':>9}{'p25':>7}{'p75':>7}")
        for cls, b in res[key].items():
            print(f"  {cls:<{w-2}}{b['articles']:>5}{b['judgments']:>8,}"
                  f"{b['judgmentLevelPct']:>8.1f}%{b['articleMedianPct']:>8.1f}%"
                  f"{b['articleP25'] if b['articleP25'] is not None else 0:>7.1f}"
                  f"{b['articleP75'] if b['articleP75'] is not None else 0:>7.1f}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
