#!/usr/bin/env python3
"""Freeze the code-ecology claim before the docket test can move it.

T3 stands: instrument identity survives every text- and article-level
reduction tried. The docket test can only sharpen or destroy that, and either
way the numbers it started from have to be visible afterwards rather than
quietly replaced. So this writes one snapshot and refuses to overwrite it.

    python3 freeze_ecology.py
    python3 freeze_ecology.py --check
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "ecology_baseline.json"


def snapshot():
    J = lambda n: json.loads((HERE / n).read_text(encoding="utf-8"))
    ins, eff = J("instruments_results.json"), J("instrument_effect_results.json")
    ai, tl = J("article_instrument_results.json"), J("twolayers_results.json")
    codes = ins["instruments"]
    return {
        "what": "the code-ecology claim as it stood before the docket test",
        "theory": "T3 --- instrument identity remains a major empirical "
                  "organizing variable after citation load, enacted-text "
                  "features, age, domain, three functional taxonomies, "
                  "article composition, matched legal function and year. It "
                  "is NOT yet a claim about legal culture: dispute "
                  "composition is the last known untested competitor.",
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("instruments.py", "instrument_effect.py",
                               "article_instrument.py")},
        "ecology": {c: {k: ins["ecology"][c][k] for k in
                        ("judgments", "hybridPct", "statuteOnlyPct",
                         "named_fiqh", "maxim", "scripture",
                         "judicial_principle", "custom",
                         "top10ConcentrationPct")}
                    for c in codes},
        "authorityVectors": ins["compositionVectors"],
        "courtVersusBar": {
            c: {"court": ins["voices"][c]["court"]["hybridPct"],
                "partyWide": (ins["voices"][c]["party_wide"] or {}).get("hybridPct"),
                "partyStrict": (ins["voices"][c]["party_strict"] or {}).get("hybridPct")}
            for c in codes},
        "matchedFunctionPairs": ai["functionMatchedPairs"],
        "articleVersusInstrument": ai["sequential"],
        "varianceRanking": ai["varianceRanking"],
        "withinBetween": ins["varianceDecomposition"]["byInstrument"],
        "yearTrajectories": {
            c: {y: v["hybridPct"] for y, v in ins["stability"][c].items()}
            for c in codes},
        "retrievalRisk": ins["retrievalRisk"],
        "traceabilityByCode": {
            c: ins["ecology"][c].get("supplementaryNamedSourcePct")
            for c in codes},
        "standardisedForCitationLoad": {
            c: eff["stratified"]["byInstrument"].get(c, {}).get("standardisedPct")
            for c in codes},
        "leaveOneOut": eff["leaveOneInstrumentOut"],
        "coreAnatomy": tl["coreAnatomy"],
    }


def main():
    live = snapshot()
    if "--check" in sys.argv:
        if not OUT.exists():
            print("no snapshot; run without --check first")
            return 1
        was = json.loads(OUT.read_text(encoding="utf-8"))
        moved = [k for k in live if k != "codeHash" and was.get(k) != live[k]]
        if moved:
            print("the frozen ecology baseline has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("ecology baseline unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the ecology baseline -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
