#!/usr/bin/env python3
"""Freeze the legal clock layer and CALIBRATION ERA 2.

The clock layer is an input to everything that follows, and it corrected two
T=0 values that Era 1 had taken from an outcome. Both the corrections and the
era they produced are written down once, with the head they were computed at,
and this script refuses to overwrite them.

    python3 freeze_clocks.py
    python3 freeze_clocks.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "legal_clock_era_1.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    c = json.loads((HERE / "clocks_results.json").read_text(encoding="utf-8"))
    e = json.loads((HERE / "transition_era2_results.json")
                   .read_text(encoding="utf-8"))
    return {
        "what": "The verified legal clock layer, and the transition era it "
                "produced. Frozen because every future transition comparison "
                "starts from these commencement dates and from the two "
                "corrections they forced.",
        "era": "LEGAL_CLOCK_ERA_1 / CALIBRATION_ERA_2",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("clocks.py", "hijri.py",
                               "transition_era2.py", "transition.py")},
        "clockQuality": c["phase5_clockQuality"],
        "eventTypes": c["phase7_eventTypes"],
        "commencementRules": c["phase6_delayedCommencement"]["rulesObserved"],
        "publicationLagEvidence": c["publicationLagEvidence"],
        "falsification": {k: v for k, v in c["phase8_falsification"].items()
                          if k not in ("byInstrument",)},
        "promotionGate": c["phase10_promotion"]["gate"],
        "promoted": c["phase10_promotion"]["promoted"],
        "clockCorrection": e["clockCorrection"],
        "era2Signatures": e["signatures"],
        "orderingResult": e["phase13_orderingSurvives"],
        "referenceSignature": e["phase26_referenceSignature"],
        "uptakeClockV2": e["phase22_uptakeClockV2"],
        "incidence": e["phase29_incidence"],
        "bet": e["phase25_bet"],
        "whatThisDoesNotTouch": "CALIBRATION ERA 1. Its signatures, its "
                                "negative controls and its S->D->F "
                                "observation stand exactly as frozen in "
                                "frozen/three_layer_baseline.json, and no "
                                "detector era is altered.",
        "whatWouldMoveThis": "a new law commencing inside a future window "
                             "with the support to read eight layers. It gets "
                             "its own era.",
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
            print("the frozen legal clock era has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("legal clock era unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the legal clock era -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
