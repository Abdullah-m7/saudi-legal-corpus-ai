#!/usr/bin/env python3
"""What does a contemporary judgment look like when it cites nothing?

12.0 per cent of reasoned judgments in the window carry no explicit authority
in the court's own voice. The earlier map read that as a fact about time --
silence is what the reforms displaced. This asks the descriptive question
instead: what distinguishes a silent judgment from a citing one *now*, with
the year held fixed.

The obvious rival explanation is measurement. A judgment can be silent
because the chamber decided without invoking anything, or because the
extractor did not recognise what it invoked, or because the publisher printed
an abridged version. The first is a fact about adjudication; the other two are
facts about this pipeline. They are separated as far as the data allows: the
length of the reasons, whether the parties cited anything in the same record,
and whether the record is one of the paired appellate ones are all measured,
and a silent judgment that is short, in a record whose parties also cite
nothing, is the profile of an abridgement rather than of a decision.

Description only. No model, and no claim that silence means anything.

    python3 silence.py
"""
import collections
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
import voice_attribution as V         # noqa: E402
from map import wilson                # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "silence_results.json"
YEARS = {1444, 1445, 1446}
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")


def main():
    index, order = M.build(REGISTRY)
    rows = []
    for rec in judgments():
        y = year_of(rec)
        if y not in YEARS:
            continue
        text, s = rec["text"], rec.get("sections") or {}
        segs = V.segments(text, s)
        reasons = [(a, b) for a, b, v in segs if v == "reasoning"]
        if not reasons:
            continue
        court = collections.Counter()
        party = collections.Counter()
        quoted = 0
        for m in A.mentions(text, s, index, order):
            if m.get("inQuote"):
                quoted += 1
                continue
            v = A.voice(m)
            if v == "court_reasoning":
                court[m["type"]] += 1
            elif v in ("party_argument", "recital"):
                party[m["type"]] += 1
        st, ns = court["statute"], sum(court[t] for t in NONSTATUTE)
        rows.append({
            "year": y,
            "courtType": rec.get("court_type") or "",
            "reasonChars": sum(b - a for a, b in reasons),
            "docChars": len(text),
            "silent": not (st or ns),
            "shape": ("hybrid" if st and ns else "statute_only" if st
                      else "nonstatute_only" if ns else "none"),
            "partyCitesAnything": bool(sum(party.values())),
            "quotedSpans": quoted,
            "paired": bool(s.get("judgmentTextofRulling")
                           and s.get("appealTextofRulling")),
        })

    n = len(rows)
    silent = [r for r in rows if r["silent"]]
    citing = [r for r in rows if not r["silent"]]

    def prof(sub):
        if not sub:
            return None
        L = sorted(r["reasonChars"] for r in sub)
        return {
            "n": len(sub),
            "medianReasonChars": L[len(L) // 2],
            "p10ReasonChars": L[len(L) // 10],
            "p90ReasonChars": L[9 * len(L) // 10],
            "partyCitesAnythingPct":
                round(100 * sum(r["partyCitesAnything"] for r in sub)
                      / len(sub), 1),
            "pairedPct": round(100 * sum(r["paired"] for r in sub)
                               / len(sub), 1),
            "meanQuotedSpans": round(
                sum(r["quotedSpans"] for r in sub) / len(sub), 2),
        }

    res = {
        "window": sorted(YEARS),
        "judgmentsWithReasons": n,
        "silentPct": round(100 * len(silent) / n, 1),
        "silentCI": wilson(len(silent), n),
        "silent": prof(silent),
        "citing": prof(citing),
        "byYear": {}, "byCourtType": {}, "byLengthDecile": [],
    }
    for y in sorted(YEARS):
        sub = [r for r in rows if r["year"] == y]
        k = sum(r["silent"] for r in sub)
        res["byYear"][str(y)] = {
            "n": len(sub), "silentPct": round(100 * k / len(sub), 1),
            "silentCI": wilson(k, len(sub))}
    ct = collections.Counter(r["courtType"] for r in rows)
    for c, _ in ct.most_common(4):
        sub = [r for r in rows if r["courtType"] == c]
        k = sum(r["silent"] for r in sub)
        res["byCourtType"][c or "(blank)"] = {
            "n": len(sub), "silentPct": round(100 * k / len(sub), 1)}
    order_ = sorted(rows, key=lambda r: r["reasonChars"])
    step = len(order_) // 10
    for i in range(10):
        sub = order_[i * step:(i + 1) * step] if i < 9 else order_[9 * step:]
        k = sum(r["silent"] for r in sub)
        res["byLengthDecile"].append({
            "decile": i + 1, "n": len(sub),
            "maxReasonChars": sub[-1]["reasonChars"],
            "silentPct": round(100 * k / len(sub), 1)})
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"{n:,} judgments with reasons in {sorted(YEARS)}; "
          f"{res['silentPct']} % cite nothing in the court's voice\n")
    print(f"{'':<26}{'silent':>12}{'citing':>12}")
    for k in ("n", "medianReasonChars", "p10ReasonChars", "p90ReasonChars",
              "partyCitesAnythingPct", "pairedPct", "meanQuotedSpans"):
        print(f"  {k:<24}{res['silent'][k]:>12,}{res['citing'][k]:>12,}")
    print("\nsilence by length decile of the reasons:")
    for d in res["byLengthDecile"]:
        print(f"   decile {d['decile']:>2}  up to {d['maxReasonChars']:>7,} "
              f"chars   silent {d['silentPct']:>5.1f}%   n={d['n']:,}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
