#!/usr/bin/env python3
"""The Contemporary Saudi Legal Reasoning Map.

What law is actually invoked in Saudi commercial adjudication now, by whom,
and in what role. One pass over the corpus; every figure is computed for each
contemporary view defined in `windows.py`.

The unit is a *mention* of legal authority, typed by `authority.py`, placed by
`voice_attribution`'s segmentation, and attributed structurally: inside the
reasons the speaker is the bench, in the recital it is whoever the cue names.
Mentions inside a passage the judgment is *quoting* are counted apart
throughout, because the words of article 164 are the legislator's and not the
court's, and conflating them was the largest error the first gold sample
found.

Six questions, in the order they can be answered:

  A  court against party    do the bench and the litigants reach for
                            different authorities?
  B  hybrid reasoning       do contemporary judgments combine statute with
                            fiqh, or has one replaced the other?
  C  silence                do reforms reduce reasoning with NO authority
                            faster than they reduce non-statutory authority?
  D  institutions           MOJ commercial courts against the tax and zakat
                            committees, on the metrics both support
  E  concentration          which instruments and articles carry contemporary
                            adjudication?
  F  the views themselves   composition, stated rather than balanced

    python3 map.py [--view contemporary_3y] [--json]
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
import voice_attribution as V         # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
OUT = HERE / "map_results.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
VOICES = ("court_reasoning", "party_argument", "recital", "operative")


def wilson(k, n, z=1.96):
    if not n:
        return [0.0, 0.0]
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round((c - r) / d * 100, 1), round((c + r) / d * 100, 1)]


def blank():
    return {
        "judgments": 0, "withReasons": 0,
        "mentions": collections.Counter(),               # type -> n
        "byVoice": collections.defaultdict(collections.Counter),
        "quoted": collections.Counter(),
        "docsWith": collections.defaultdict(set),        # type -> judgment ids
        "courtDocsWith": collections.defaultdict(set),
        "partyDocsWith": collections.defaultdict(set),
        "hybrid": 0, "statuteOnly": 0, "nonStatuteOnly": 0, "noAuthority": 0,
        "instrument": collections.Counter(),
        "article": collections.Counter(),
        "procedural": collections.Counter(),
        "articleUnparsed": 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    index, order = M.build(REGISTRY)
    acc = {name: blank() for name in VIEWS}
    # question C is a claim about change, and change cannot be read off two
    # overlapping views whose year mixes differ. The per-year series carries
    # the selection control beside it, because whether a circuit writes its
    # own reasons moved from 2 per cent to 86 per cent across this corpus and
    # everything else here is conditioned on it.
    byyear = collections.defaultdict(blank)

    for rec in judgments():
        y = year_of(rec)
        views = [n for n, ys in VIEWS.items() if y in ys]
        if not views:
            continue
        text, sections = rec["text"], rec.get("sections") or {}
        ms = A.mentions(text, sections, index, order)
        spans = V.segments(text, sections)
        reasoned = any(v == "reasoning" for _, _, v in spans)

        # per-judgment court-reasoning profile, the unit questions B and C need
        court_types = set()
        for m in ms:
            if A.voice(m) == "court_reasoning" and not m.get("inQuote"):
                court_types.add(m["type"])
        has_stat = "statute" in court_types
        has_non = bool(court_types & set(NONSTATUTE))

        for name in list(views) + ([f"Y{y}"] if y else []):
            b = acc[name] if name in acc else byyear[name]
            b["judgments"] += 1
            b["withReasons"] += reasoned
            if reasoned:
                if has_stat and has_non:
                    b["hybrid"] += 1
                elif has_stat:
                    b["statuteOnly"] += 1
                elif has_non:
                    b["nonStatuteOnly"] += 1
                else:
                    b["noAuthority"] += 1
            for m in ms:
                t, vc = m["type"], A.voice(m)
                if m.get("inQuote"):
                    b["quoted"][t] += 1
                    continue
                b["mentions"][t] += 1
                b["byVoice"][vc][t] += 1
                b["docsWith"][t].add(rec["id"])
                if vc == "court_reasoning":
                    b["courtDocsWith"][t].add(rec["id"])
                    if t == "statute" and m["instrument"]:
                        b["instrument"][m["instrument"]] += 1
                        # «١٦», «16», «السادسة عشرة» and «السادسة عشر» are one
                        # article. Without this the concentration figure is an
                        # artefact of orthography rather than a fact about law.
                        num, _ = AO.parse(m["article"] or "")
                        if num is not None:
                            b["article"][(m["instrument"], num)] += 1
                        else:
                            b["articleUnparsed"] += 1
                        b["procedural"]["procedural" if m["procedural"]
                                        else "substantive"] += 1
                elif vc == "party_argument":
                    b["partyDocsWith"][t].add(rec["id"])

    out = {"views": {}, "byYear": {}}
    for name, b in list(acc.items()) + list(byyear.items()):
        n, r = b["judgments"], b["withReasons"]
        tot = sum(b["mentions"].values()) or 1
        court_tot = sum(b["byVoice"]["court_reasoning"].values()) or 1
        party_tot = sum(b["byVoice"]["party_argument"].values()) or 1
        proc = b["procedural"]["procedural"]
        proc_tot = proc + b["procedural"]["substantive"] or 1
        target = out["views"] if name in acc else out["byYear"]
        target[name] = {
            "judgments": n, "withReasons": r,
            "mentionsTotal": sum(b["mentions"].values()),
            "quotedTotal": sum(b["quoted"].values()),
            "typeShare": {t: round(100 * b["mentions"][t] / tot, 1)
                          for t in A.TYPES},
            "courtShare": {t: round(100 * b["byVoice"]["court_reasoning"][t]
                                    / court_tot, 1) for t in A.TYPES},
            "partyShare": {t: round(100 * b["byVoice"]["party_argument"][t]
                                    / party_tot, 1) for t in A.TYPES},
            "voiceTotals": {v: sum(b["byVoice"][v].values()) for v in VOICES},
            "hybridRate": round(100 * b["hybrid"] / r, 1) if r else None,
            "statuteOnlyRate": round(100 * b["statuteOnly"] / r, 1) if r else None,
            "nonStatuteOnlyRate": round(100 * b["nonStatuteOnly"] / r, 1) if r else None,
            "noAuthorityRate": round(100 * b["noAuthority"] / r, 1) if r else None,
            "hybridCI": wilson(b["hybrid"], r),
            "noAuthorityCI": wilson(b["noAuthority"], r),
            "proceduralShareOfCourtStatute": round(100 * proc / proc_tot, 1),
            "topInstruments": [[k, v] for k, v in b["instrument"].most_common(12)],
            "topArticles": [[f"{k[0]} art.{k[1]}", v]
                            for k, v in b["article"].most_common(15)],
            "articleNumberUnparsed": b["articleUnparsed"],
            "instrumentConcentration": {
                f"top{k}": round(100 * sum(v for _, v in
                                           b["instrument"].most_common(k))
                                 / (sum(b["instrument"].values()) or 1), 1)
                for k in (1, 3, 5, 10)},
            "articleConcentration": {
                f"top{k}": round(100 * sum(v for _, v in
                                           b["article"].most_common(k))
                                 / (sum(b["article"].values()) or 1), 1)
                for k in (5, 10, 20, 50)},
            "distinctArticlesInCourtReasoning": len(b["article"]),
        }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    for name in VIEWS:
        v = out["views"][name]
        print(f"\n{'='*72}\n{name}   {v['judgments']:,} judgments, "
              f"{v['withReasons']:,} with reasons")
        print(f"  {v['mentionsTotal']:,} authority mentions "
              f"(+{v['quotedTotal']:,} inside quoted passages, held apart)")
        print(f"\n  {'type':<20}{'all':>8}{'court reasons':>16}{'party argument':>17}")
        for t in A.TYPES:
            print(f"  {t:<20}{v['typeShare'][t]:>7.1f}%"
                  f"{v['courtShare'][t]:>15.1f}%{v['partyShare'][t]:>16.1f}%")
        print(f"\n  judgments with reasons, by what the BENCH invokes:")
        print(f"    statute and non-statute together  "
              f"{v['hybridRate']:>6.1f}%  {v['hybridCI']}")
        print(f"    statute alone                     {v['statuteOnlyRate']:>6.1f}%")
        print(f"    non-statute alone                 {v['nonStatuteOnlyRate']:>6.1f}%")
        print(f"    no explicit authority at all      "
              f"{v['noAuthorityRate']:>6.1f}%  {v['noAuthorityCI']}")
        print(f"  procedural share of the bench's statute citations "
              f"{v['proceduralShareOfCourtStatute']:.1f}%")
    print(f"\n{'='*72}\nquestion C, by year, with the selection control beside it")
    print(f"{'year':<7}{'judgments':>11}{'reasoned %':>12}{'hybrid %':>10}"
          f"{'statute only':>14}{'non-stat only':>15}{'NO authority':>14}")
    for k in sorted(out["byYear"]):
        v = out["byYear"][k]
        if v["withReasons"] < 200:
            continue
        share = 100 * v["withReasons"] / v["judgments"]
        print(f"{k[1:]:<7}{v['judgments']:>11,}{share:>12.1f}"
              f"{v['hybridRate']:>10.1f}{v['statuteOnlyRate']:>14.1f}"
              f"{v['nonStatuteOnlyRate']:>15.1f}{v['noAuthorityRate']:>14.1f}")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
