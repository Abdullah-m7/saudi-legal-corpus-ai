#!/usr/bin/env python3
"""Freeze what this repository expects, before the answer arrives.

The nowcast is re-run whenever the corpus grows; that is the point of it. What
must NOT move is the set of expectations committed to at a given moment: the
issued forecasts and their scoring rules, the branch falsifiers, the AI
hypothesis tournament, the first-case capture schema, and the anchors those
were reasoned from.

This is the file a future session is scored against.

    python3 freeze_nowcast.py
    python3 freeze_nowcast.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "nowcast_era_1.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    n = json.loads((HERE / "nowcast_results.json").read_text(encoding="utf-8"))
    f = json.loads((HERE / "futures_results.json").read_text(encoding="utf-8"))
    return {
        "what": "NOWCAST_ERA_1. The expectations committed to at this "
                "endpoint, with the current state they were reasoned from.",
        "era": "NOWCAST_ERA_1",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "codeHash": {n_: hashlib.sha256((HERE / n_).read_bytes()).hexdigest()[:12]
                     for n_ in ("nowcast.py", "futures.py")},
        "currentMaturePeriod": n["part1_windows"]["CURRENT_MATURE_PERIOD"],
        "observationLag": n["part1_windows"]["observationLag"],
        "currentStateAtFreeze": n["part1_currentState"]["CURRENT_12_MONTHS"],
        "issuedForecasts": n["part15_forecasts"],
        "retrievalArchitectures": n["part18_retrievalArchitectures"],
        "branches": f["part5_16_branches"],
        "hypothesisTournament": f["part17_hypothesisTournament"],
        "aiAnchors": json.loads(
            (HERE / "ai_law_map.json").read_text(encoding="utf-8"))["anchors"],
        "aiIssueFamilies": json.loads(
            (HERE / "ai_law_map.json").read_text(encoding="utf-8"))[
                "issueFamilies"],
        "firstCaseReadiness": f["part8_firstCaseReadiness"],
        "aiComponents": f["part10_aiComponents"],
        "aiBaseline": f["part16_aiBaseline"],
        "liveChain": f["part23_liveChain"],
        "surpriseReadiness": f["part22_surpriseReadiness"],
        "currentSignals": f["part3_currentOfficialSignalPass"]["items"],
        "scoringDiscipline": "a forecast here is scored against the realised "
                             "value at its stated horizon, under the regime "
                             "assumption recorded with it. A regime break "
                             "does not excuse a miss; it changes the status "
                             "to REGIME_BREAK_BEFORE_TARGET, and that status "
                             "is set by the frozen regime detector, not by "
                             "the outcome.",
        "whatThisDoesNotTouch": "every earlier frozen era stands: the "
                                "doctrinal diffusion baseline, the formula "
                                "baseline, the three-layer baseline, the "
                                "legal clock era and the regime detector "
                                "era, along with all three detector eras.",
        "whatWouldMoveThis": "nothing. A later endpoint gets NOWCAST_ERA_2 "
                             "and this file remains what was expected here.",
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
            print("the frozen nowcast era has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("nowcast era unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the nowcast era -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
