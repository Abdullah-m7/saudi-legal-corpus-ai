#!/usr/bin/env python3
"""Freeze the formula-layer baseline that FORMULA_DETECTOR_ERA_1 scores against.

PHASE 20 of the recurring-formula programme is a concentration baseline, and a
baseline that moves with the analysis is not a baseline. The detector era arms
four metrics against these values; if a later session re-runs the analysis on a
wider window, the numbers a future confirmed shift is judged against have to be
the ones written here, not whatever the re-run produced.

    python3 freeze_formula.py
    python3 freeze_formula.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "formula_baseline.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    d = json.loads((HERE / "formula_analysis_results.json")
                   .read_text(encoding="utf-8"))
    return {
        "what": "The recurring-legal-formula layer as first measured: the "
                "unit, the concentration baseline, the detector era's armed "
                "metrics, and the ablation result that reinterprets the "
                "frozen de-boilerplating control.",
        "era": "FORMULA_ERA_1",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("formula.py", "formula_analysis.py")},
        "unit": {k: d["phase2_unitSpecification"][k] for k in
                 ("definition", "contextRadius", "exactOrNearExact",
                  "articleNumbersPreserved", "windowTokens")},
        "circulatingFormulas": d["phase3_exactVersusFamily"]["exactFormulas"],
        "familyGroupingVerdict":
            d["phase3_exactVersusFamily"]["stability"]["verdict"],
        "sourceMaskingVerdict": d["phase4_sourceMasking"]["verdict"],
        "multiSourceShells":
            d["phase4_sourceMasking"]["shellsWithMoreThanOneSource"],
        "taxonomy": d["phase6_formulaClasses"]["byClass"],
        "concentration": {k: d["phase20_21_concentration"][k] for k in
                          ("ALL", "COURT", "BAR", "CIRCULATING_ONLY",
                           "PROCEDURAL_GROUP", "DOCTRINAL_GROUP",
                           "courtVersusBarDiversity")},
        "mobility": {
            "formulaCirculatingOnly":
                d["phase22_threeLayerMobility"]["formulaLayerCirculatingOnly"],
            "formulaAll": {k: d["phase22_threeLayerMobility"]["formulaLayer"][k]
                           for k in ("rankAutocorrelation",
                                     "topDecilePersistence",
                                     "bottomHalfToTopDecileMobility",
                                     "universeSize")}},
        "detectorEra": d["phase27_formulaDetectorEra1"],
        "ablation": {
            "baselineVerdict":
                d["phase9_classSpecificAblation"]["baselineVerdict"],
            "allRemovedVerdict":
                d["phase9_classSpecificAblation"]["allRemovedVerdict"],
            "singleClassRemovalsThatReproduceTheFlip":
                d["phase9_classSpecificAblation"][
                    "singleClassRemovalsThatReproduceTheFlip"],
            "randomRemovalFlipShares": {
                k: v["flipShare"] for k, v in
                sorted(d["phase9b_volumeControl"]["arms"].items())},
            "verdict": d["decisions"]["headlineVerdict"]},
        "whatThisDoesNotFreeze": "the frozen doctrinal diffusion era. Its "
                                 "numbers stand exactly as they were; what "
                                 "changes is what the de-boilerplating "
                                 "control is understood to have measured.",
    }


def main():
    live = snapshot()
    if "--check" in sys.argv:
        if not OUT.exists():
            print("no snapshot; run without --check first")
            return 1
        was = json.loads(OUT.read_text(encoding="utf-8"))
        skip = {"codeHash", "repositoryHead", "frozenAt"}
        moved = [k for k in live if k not in skip and was.get(k) != live[k]]
        if moved:
            print("the frozen formula baseline has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("formula baseline unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the formula baseline -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
