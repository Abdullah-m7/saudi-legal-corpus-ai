#!/usr/bin/env python3
"""Two questions the completeness test cannot answer, and one it provoked.

1. DENOMINATORS. "Statutory prevalence rises, fiqh prevalence is flat" was
   computed on one denominator -- reasoned judgments. A share can be made to
   rise or fall by choosing what to divide by, so the honest form of the claim
   is all five denominators printed together, and an explanation wherever they
   disagree.

2. THE CIVIL TRANSACTIONS LAW. It is the most important substantive
   codification in the corpus and it commenced within the window. Where does
   the bench still reason past it, article by article?

3. THE EVIDENCE LAW AS A CONTRAST. Both are recent, both are substantive,
   and they organise different work: one allocates proof, the other creates
   entitlements. If hybrid reasoning has a shape, these two should not have
   the same one.

    python3 codes.py
"""
import collections
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
from map import wilson                       # noqa: E402

LAYER = HERE / "authority_mentions.jsonl.gz"
DOCS = HERE / "authority_layer.jsonl.gz"
GOLD = HERE / "completeness_gold.json"
OUT = HERE / "codes_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
YEARS = (1442, 1443, 1444, 1445, 1446)
POST_CTL = (1445, 1446)


def corpus():
    """Every judgment in the window: year, and whether it carries reasons."""
    out = {}
    with gzip.open(DOCS, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r["year"] not in YEARS:
                continue
            out[r["judgment"]] = (r["year"], bool(r.get("reasoned")))
    return out


def court_layer():
    out = collections.defaultdict(
        lambda: [collections.Counter(), set(), 0])
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            if r["role"] != "court_reasoning":
                continue
            d = out[r["j"]]
            d[0][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[1].add((r["inst"], r["art"]))
    return out


def party_layer(wide):
    roles = {"party_argument", "recital"} if wide else {"party_argument"}
    out = collections.defaultdict(
        lambda: [collections.Counter(), set()])
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q") or r["role"] not in roles:
                continue
            d = out[r["j"]]
            d[0][r["t"]] += 1
            if r.get("inst") and r.get("art") is not None:
                d[1].add((r["inst"], r["art"]))
    return out


def denominators(docs, court):
    """PHASE 13: the same fact, divided five ways."""
    rows = {}
    for y in YEARS:
        alls = [j for j, (yy, _) in docs.items() if yy == y]
        reas = [j for j in alls if docs[j][1]]
        fq = sum(court[j][0]["fiqh_source"] for j in alls if j in court)
        st = sum(court[j][0]["statute"] for j in alls if j in court)
        nonst = sum(sum(court[j][0][t] for t in NONSTATUTE)
                    for j in alls if j in court)
        dj = sum(1 for j in alls if j in court and court[j][0]["fiqh_source"])
        dr = sum(1 for j in reas if j in court and court[j][0]["fiqh_source"])
        rows[str(y)] = {
            "judgments": len(alls), "reasoned": len(reas),
            "fiqhPrevalenceAllJudgmentsPct": round(100 * dj / len(alls), 1),
            "fiqhPrevalenceAllCI": wilson(dj, len(alls)),
            "fiqhPrevalenceReasonedPct":
                round(100 * dr / len(reas), 1) if reas else None,
            "fiqhPrevalenceReasonedCI": wilson(dr, len(reas)),
            "fiqhCitationsPer1000Judgments": round(1000 * fq / len(alls), 1),
            "fiqhCitationsPer1000Reasoned":
                round(1000 * fq / len(reas), 1) if reas else None,
            "fiqhPerStatutoryCitation": round(fq / st, 3) if st else None,
            "nonStatutePerStatutoryCitation": round(nonst / st, 3) if st else None,
            "statuteCitations": st, "fiqhCitations": fq,
        }
    return rows


def code_profile(docs, court, party, wide, instrument, years, minimum):
    """PHASES 11 and 12: article by article inside one statute book."""
    keep = {j for j, (y, _) in docs.items() if y in years}
    n = collections.Counter()
    hit = collections.Counter()
    typed = collections.defaultdict(collections.Counter)
    for j in keep:
        if j not in court:
            continue
        types, arts, _ = court[j]
        mixed = any(types[t] for t in NONSTATUTE)
        for a in arts:
            if a[0] != instrument:
                continue
            n[a] += 1
            if mixed:
                hit[a] += 1
            for t in NONSTATUTE:
                if types[t]:
                    typed[a][t] += 1
            # a judgment citing both a verse and a hadith is one judgment,
            # not two; summing the two type counts put art. 91 at 140 %.
            if types["quran"] or types["hadith"]:
                typed[a]["scripture"] += 1
    pn = collections.Counter()
    ph = collections.Counter()
    for j in keep:
        if j not in party:
            continue
        types, arts = party[j]
        mixed = any(types[t] for t in NONSTATUTE)
        for a in arts:
            if a[0] != instrument:
                continue
            pn[a] += 1
            if mixed:
                ph[a] += 1
    gold = json.loads(GOLD.read_text(encoding="utf-8"))["labels"]
    rows = []
    for a in sorted(n, key=lambda a: -n[a]):
        if n[a] < minimum:
            continue
        rows.append({
            "article": a[1], "courtJudgments": n[a],
            "nonStatutePct": round(100 * hit[a] / n[a], 1),
            "namedFiqhPct": round(100 * typed[a]["fiqh_source"] / n[a], 1),
            "maximPct": round(100 * typed[a]["legal_maxim"] / n[a], 1),
            "scripturePct": round(100 * typed[a]["scripture"] / n[a], 1),
            "judicialPrinciplePct": round(
                100 * typed[a]["judicial_principle"] / n[a], 1),
            "customPct": round(100 * typed[a]["custom"] / n[a], 1),
            "partyJudgments": pn[a],
            "partyNonStatutePct":
                round(100 * ph[a] / pn[a], 1) if pn[a] >= 20 else None,
            "completenessClass":
                (gold.get(f"{instrument}:{a[1]}") or {}).get("class"),
        })
    tot = sum(n[a] for a in n)
    got = sum(hit[a] for a in n)
    return {"instrument": instrument, "years": list(years),
            "minCourtJudgments": minimum,
            "distinctArticlesCited": len(n),
            "courtCitingJudgments": tot,
            "pooledNonStatutePct": round(100 * got / tot, 1) if tot else None,
            "pooledCI": wilson(got, tot),
            "partyVoice": "wide" if wide else "strict",
            "articles": rows}


def main():
    docs, court = corpus(), court_layer()
    party = party_layer(wide=True)
    res = {
        "denominators": denominators(docs, court),
        "civilTransactionsLaw": code_profile(
            docs, court, party, True, "civil_transactions_law", POST_CTL, 10),
        "civilTransactionsLaw5y": code_profile(
            docs, court, party, True, "civil_transactions_law", YEARS, 15),
        "evidenceLaw": code_profile(
            docs, court, party, True, "evidence_law", POST_CTL, 20),
        "evidenceLaw5y": code_profile(
            docs, court, party, True, "evidence_law", YEARS, 40),
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")

    print("PHASE 13 --- the same fact, five denominators\n")
    print(f"{'year':<6}{'judg':>7}{'reasoned':>10}{'fiqh prev all':>15}"
          f"{'fiqh prev reas':>16}{'fiqh/1k judg':>14}{'fiqh/1k reas':>14}"
          f"{'fiqh/statute':>14}")
    for y, r in res["denominators"].items():
        print(f"{y:<6}{r['judgments']:>7,}{r['reasoned']:>10,}"
              f"{r['fiqhPrevalenceAllJudgmentsPct']:>14.1f}%"
              f"{r['fiqhPrevalenceReasonedPct']:>15.1f}%"
              f"{r['fiqhCitationsPer1000Judgments']:>14.1f}"
              f"{r['fiqhCitationsPer1000Reasoned']:>14.1f}"
              f"{r['fiqhPerStatutoryCitation']:>14.3f}")
    for k in ("civilTransactionsLaw", "evidenceLaw"):
        v = res[k]
        print(f"\n{k}  {v['years']}  {v['distinctArticlesCited']} articles "
              f"cited, {v['courtCitingJudgments']:,} judgments, pooled "
              f"non-statutory {v['pooledNonStatutePct']} %")
        for r in v["articles"][:10]:
            print(f"   art.{r['article']:<5}n={r['courtJudgments']:>5} "
                  f"nonstat {r['nonStatutePct']:>5.1f}%  fiqh "
                  f"{r['namedFiqhPct']:>5.1f}%  maxim {r['maximPct']:>5.1f}%  "
                  f"scripture {r['scripturePct']:>5.1f}%  "
                  f"{r['completenessClass'] or ''}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
