#!/usr/bin/env python3
"""How much of the authority a contemporary court uses can be looked up?

Two questions that turn out to be one.

PHASE 17, the retrieval question. Three candidate universes for a Saudi legal
assistant -- the statute book, whole published judgments, and the
court-reasoning layer this repository builds -- and for each, mechanically:
does the authority the court actually used exist in that universe at all? No
model is built and nothing is generated; this is set membership.

PHASES 18-19, the traceability question. Underneath the retrieval problem is
a harder one. An «المقرر فقهاً وقضاءً» names no jurist, no book and no page.
It cannot be retrieved from any corpus, however complete, because the judgment
does not say what to retrieve. That is not a criticism of drafting practice --
a chamber writing for the parties has no reason to supply a citation an
outside researcher could follow. It is a measurable property of the record,
and it bounds what any downstream system or replication can do.

Four traceability classes, assigned from the extractor's own rule id, so the
assignment is mechanical and auditable rather than a judgment:

    RESOLVED_STATUTE   a statute whose instrument and article both resolved
    UNRESOLVED_STATUTE a statutory citation whose article did not resolve
    NAMED_SOURCE       a jurist, a book, a named maxim, a verse, a hadith
    UNNAMED            «المقرر فقهاً», «المستقر شرعاً», a settled practice,
                       a trade custom, an unnamed maxim: no source to follow

    python3 traceability.py
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
OUT = HERE / "traceability_results.json"
YEARS = (1442, 1443, 1444, 1445, 1446)
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")

# rule id -> traceability class. Every rule in authority.py is placed.
NAMED = {"fiqh.book", "fiqh.jurist", "maxim.named", "quran.citation",
         "hadith.citation", "contract.article", "contract.clause"}
UNNAMED = {"fiqh.unattributed", "maxim.text", "principle.settled",
           "custom.trade", "discretion.named", "contract.possessive"}


def klass(r):
    if r["t"] == "statute":
        return ("RESOLVED_STATUTE" if r.get("inst") and r.get("art") is not None
                else "UNRESOLVED_STATUTE")
    return "NAMED_SOURCE" if r["r"] in NAMED else "UNNAMED"


def main():
    fn = json.loads(FUNC.read_text(encoding="utf-8"))["labels"]
    by_year = collections.defaultdict(collections.Counter)
    by_kind = collections.defaultdict(collections.Counter)
    by_inst = collections.defaultdict(collections.Counter)
    by_func = collections.defaultdict(collections.Counter)
    docs = collections.defaultdict(
        lambda: {"court": collections.Counter(),
                 "courtRules": collections.Counter(),
                 "all": 0, "y": 0, "insts": set(), "funcs": set()})
    with gzip.open(LAYER, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r.get("q"):
                continue
            d = docs[r["j"]]
            d["y"] = r["y"]
            d["all"] += 1
            if r["role"] != "court_reasoning":
                continue
            k = klass(r)
            d["court"][k] += 1
            d["courtRules"][r["t"]] += 1
            by_year[r["y"]][k] += 1
            by_kind[r["t"]][k] += 1
            if r.get("inst"):
                d["insts"].add(r["inst"])
                by_inst[r["inst"]][k] += 1
                if r.get("art") is not None:
                    lab = fn.get(f"{r['inst']}:{r['art']}")
                    if lab:
                        d["funcs"].add(lab["function"])
    for j, d in docs.items():
        for f in d["funcs"]:
            for k, v in d["court"].items():
                by_func[f][k] += v

    def pct(c):
        t = sum(c.values())
        return {"mentions": t,
                **{k: round(100 * c[k] / t, 1) for k in
                   ("RESOLVED_STATUTE", "UNRESOLVED_STATUTE",
                    "NAMED_SOURCE", "UNNAMED")}} if t else None

    live = [d for d in docs.values() if sum(d["court"].values())]
    tot = collections.Counter()
    for d in live:
        tot.update(d["court"])
    nonstat = sum(sum(v.values()) for k, v in by_kind.items()
              if k in NONSTATUTE)

    # PHASE 17: coverage of the three retrieval universes.
    reasoned = len(live)
    st_only = sum(1 for d in live
                  if d["court"]["RESOLVED_STATUTE"] + d["court"]["UNRESOLVED_STATUTE"]
                  and not any(d["courtRules"][t] for t in NONSTATUTE))
    mixed = sum(1 for d in live
                if d["court"]["RESOLVED_STATUTE"] + d["court"]["UNRESOLVED_STATUTE"]
                and any(d["courtRules"][t] for t in NONSTATUTE))
    nonstat_only = reasoned - st_only - mixed
    court_share = [d for d in live if d["all"]]
    precision_b = round(
        100 * sum(sum(d["court"].values()) for d in court_share)
        / sum(d["all"] for d in court_share), 1)

    res = {
        "window": list(YEARS),
        "judgmentsWithCourtAuthority": reasoned,
        "courtMentions": sum(tot.values()),
        "overall": pct(tot),
        "byYear": {str(y): pct(by_year[y]) for y in YEARS if by_year[y]},
        "byAuthorityType": {k: pct(v) for k, v in sorted(by_kind.items())},
        "byInstrument": {k: pct(v) for k, v in sorted(
            by_inst.items(), key=lambda kv: -sum(kv[1].values()))[:8]},
        "byArticleFunction": {k: pct(v) for k, v in sorted(by_func.items())},
        "nonStatutoryMentions": nonstat,
        "retrievalUniverses": {
            "note": "coverage is set membership, not model performance. "
                    "Universe C is derived from the judgment itself, so its "
                    "coverage is 100 per cent by construction; what it buys "
                    "is precision, and the number below is what a "
                    "whole-document universe gives up.",
            "A_statute_book": {
                "judgmentsFullyCoveredPct": round(100 * st_only / reasoned, 1),
                "judgmentsPartlyCoveredPct": round(100 * mixed / reasoned, 1),
                "judgmentsNotCoveredPct":
                    round(100 * nonstat_only / reasoned, 1),
                "mentionCoveragePct": round(
                    100 * (tot["RESOLVED_STATUTE"] + tot["UNRESOLVED_STATUTE"])
                    / sum(tot.values()), 1)},
            "B_whole_judgments": {
                "mentionCoveragePct": 100.0,
                "precisionPct": precision_b,
                "meaning": "every authority the court used is inside the "
                           "document, but only this share of the authority "
                           "IN the document is the court's; the rest is "
                           "recital and party argument"},
            "C_court_reasoning_layer": {
                "mentionCoveragePct": 100.0, "precisionPct": 100.0},
        },
    }

    # PHASE 19: per-judgment traceable share, as components not a score.
    shares = []
    for d in live:
        t = sum(d["court"].values())
        good = d["court"]["RESOLVED_STATUTE"] + d["court"]["NAMED_SOURCE"]
        shares.append(100 * good / t)
    shares.sort()
    fully = sum(1 for s in shares if s == 100)
    res["perJudgment"] = {
        "definition": "share of the court's own authority mentions that a "
                      "reader could follow from the citation alone: a "
                      "resolved statutory article, or a named jurist, book, "
                      "maxim, verse or hadith",
        "medianPct": round(shares[len(shares) // 2], 1),
        "p25Pct": round(shares[len(shares) // 4], 1),
        "meanPct": round(sum(shares) / len(shares), 1),
        "fullyTraceablePct": round(100 * fully / len(shares), 1),
        "fullyTraceableCI": wilson(fully, len(shares)),
        "caution": "this is a property of the citation as published, not of "
                   "the reasoning. A chamber writing for the parties has no "
                   "reason to supply a citation an outside researcher could "
                   "follow, and nothing here says it should.",
    }
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    o = res["overall"]
    print(f"{res['courtMentions']:,} authority mentions in the court's voice")
    print(f"  resolved statute {o['RESOLVED_STATUTE']} %   unresolved statute "
          f"{o['UNRESOLVED_STATUTE']} %   named source {o['NAMED_SOURCE']} %   "
          f"unnamed {o['UNNAMED']} %")
    print("\nby authority type (share of that type's mentions):")
    for k, v in res["byAuthorityType"].items():
        if v:
            print(f"   {k:<20}{v['mentions']:>7,}  named {v['NAMED_SOURCE']:>5.1f}%"
                  f"   unnamed {v['UNNAMED']:>5.1f}%")
    print("\nby article function of what the judgment was citing:")
    for k, v in res["byArticleFunction"].items():
        print(f"   {k:<26}{v['mentions']:>8,}  named {v['NAMED_SOURCE']:>5.1f}%"
              f"   unnamed {v['UNNAMED']:>5.1f}%")
    a = res["retrievalUniverses"]["A_statute_book"]
    print(f"\nstatute book covers all of the court's authority in "
          f"{a['judgmentsFullyCoveredPct']} % of judgments, part of it in "
          f"{a['judgmentsPartlyCoveredPct']} %, none in "
          f"{a['judgmentsNotCoveredPct']} %")
    print(f"whole judgments: everything is there, but only "
          f"{res['retrievalUniverses']['B_whole_judgments']['precisionPct']} % "
          f"of the authority in a document is the court's")
    p = res["perJudgment"]
    print(f"\nper judgment, median {p['medianPct']} % of the court's authority "
          f"is followable from the citation; {p['fullyTraceablePct']} % of "
          f"judgments are fully traceable")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
