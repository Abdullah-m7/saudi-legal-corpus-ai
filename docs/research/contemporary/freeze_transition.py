#!/usr/bin/env python3
"""Freeze the three-layer inputs and the first transition signatures.

PHASE 1 of the transition-sequencing programme takes the statutory, doctrinal
and formula layers as INPUTS. They are quoted from results that already exist
and are not recomputed here. Freezing them matters because the whole point of
the programme is to compare a FUTURE transition against historical bounds, and
bounds that move with a re-run are not bounds.

The two calibration signatures are frozen with them, including the
uncomfortable part: they are backfilled, there are two of them, and the
negative control shows the battery separates arrivals from non-arrivals rather
than events from non-events.

    python3 freeze_transition.py
    python3 freeze_transition.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "three_layer_baseline.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    t = json.loads((HERE / "transition_results.json").read_text(encoding="utf-8"))
    return {
        "what": "The three measured layers as inputs, and the first two "
                "transition signatures measured through them. The reference "
                "a future transition -- AI-linked or not -- is compared "
                "against.",
        "era": "TRANSITION_ERA_1",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("transition.py", "formula.py",
                               "companions.py")},
        "scopeCorrections": t["scopeCorrections"],
        "threeLayerBaselines": t["phase1_threeLayerBaselines"],
        "layerStack": t["phase5_6_layerStack"],
        "uptakeRule": {
            "arrivalsConsidered": t["phase14_uptakeCalibration"]["arrivalsConsidered"],
            "chosenRepeatedRule": t["phase14_uptakeCalibration"]["chosenRepeatedRule"],
            "chosenSustainedRule": t["phase14_uptakeCalibration"]["chosenSustainedRule"],
            "candidateRules": t["phase14_uptakeCalibration"]["candidateRules"]},
        "signatures": t["phase20_21_signatures"],
        "negativeControl": {k: v for k, v in
                            t["phase19_pseudoEventControls"].items()
                            if k != "rows"},
        "formulaFirstTest": t["phase9_formulaFirstTest"],
        "speedBands": t["phase28_speedBands"],
        "aiChannelHypotheses": t["phase23_aiChannelHypotheses"],
        "identificationRule": t["phase25_identificationRule"],
        "evaluationHorizonQuarters": t["phase27_eventWithoutSignal"][
            "horizonQuarters"],
        "whatThisFreezes": "the bounds, the thresholds, the layer criteria "
                           "and the two calibration signatures. NOT the "
                           "detectors of any earlier era, which are untouched.",
        "whatWouldMoveThis": "a third calibration transition with a known "
                             "legal clock. It gets its own era; this file is "
                             "not rewritten.",
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
            print("the frozen three-layer baseline has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("three-layer baseline unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the three-layer baseline -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
