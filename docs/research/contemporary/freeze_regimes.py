#!/usr/bin/env python3
"""Freeze REGIME_DETECTOR_ERA_1 before any future quarter exists.

The point of a regime detector is to notice that the process generating the
observations has changed. A detector whose thresholds can be adjusted after
seeing a result cannot do that: it can only ratify a story. So the methods,
the significance level, the permutation seed, the minimum segment length, the
escalation rule and the measured false-alarm behaviour are written down once,
here, and this script refuses to overwrite them.

    python3 freeze_regimes.py
    python3 freeze_regimes.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "regime_detector_era_1.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    r = json.loads((HERE / "regimes_results.json").read_text(encoding="utf-8"))
    coh = r["phase24_coherence"]
    return {
        "what": "REGIME_DETECTOR_ERA_1. The contract for deciding that the "
                "data-generating process has changed, with the false-alarm "
                "behaviour it was calibrated against.",
        "era": "REGIME_DETECTOR_ERA_1",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("regimes.py",)},
        "contract": r["phase25_regimeDetectorEra1"],
        "seriesTested": r["phase5_seriesTested"],
        "falseAlarm": r["phase21_falseAlarm"],
        "observedCoherence": {k: v for k, v in coh.items()
                              if k != "candidates"},
        "observedCandidates": coh["candidates"],
        "crossReference": {k: v for k, v in r["phase7_8_crossReference"].items()
                           if k != "BREAK_WITH_A_NEARBY_EVENT"},
        "withinRegimeForecastability": {
            "verdict": r["phase15_withinRegimeForecastability"]["verdict"],
            "seriesTested":
                r["phase15_withinRegimeForecastability"]["seriesTested"],
            "seriesWhereSegmentationWins":
                r["phase15_withinRegimeForecastability"][
                    "seriesWhereSegmentationWins"]},
        "retrievalAgeing": {k: v for k, v in
                            r["phase16_regimeAwareRetrievalAgeing"].items()
                            if k != "perStep"},
        "correction": r["correction"],
        "whatThisDoesNotTouch": "PROSPECTIVE_DETECTOR_ERA_1, "
                                "DOCTRINAL_DETECTOR_ERA_2, "
                                "FORMULA_DETECTOR_ERA_1, the transition eras "
                                "and the legal clock era. All are untouched "
                                "and all are now read as within-regime "
                                "baselines.",
        "whatWouldMoveThis": "nothing about this file. A future candidate "
                             "break is recorded against this contract, not by "
                             "editing it.",
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
            print("the frozen regime detector era has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("regime detector era unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the regime detector era -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
