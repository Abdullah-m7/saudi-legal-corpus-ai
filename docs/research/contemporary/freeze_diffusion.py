#!/usr/bin/env python3
"""Freeze the doctrinal diffusion result before the formula programme starts.

The result being frozen is uncomfortable and that is exactly why it is frozen:
the largest unmatched contrast in the programme -- doctrinal sources first
observed in the court's voice persist at 0.5882 against bar-first 0.2857 --
dissolves under de-boilerplating, and the matched verdict flips to
BAR_FIRST_NOT_WORSE_AFTER_MATCHING.

The next programme asks what those recurring formulas ARE. That question can
end in any of three places: the formulas are empty boilerplate and the
de-boilerplated numbers are the honest ones; the formulas carry legal
propositions and removing them removed signal; or the two cannot be separated.
All three are live. None of them may be allowed to quietly re-write the
numbers above, so the numbers above are written down first, with the head they
were computed at, and this script refuses to overwrite them.

    python3 freeze_diffusion.py
    python3 freeze_diffusion.py --check
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "frozen" / "doctrinal_diffusion_era_1.json"


def head():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNKNOWN"


def snapshot():
    d = json.loads((HERE / "diffusion_results.json").read_text(encoding="utf-8"))
    surv = d["phase5_6_survivalByFirstMover"]["CODE"]
    boil = d["phase16_deBoilerplated"]
    return {
        "what": "The DOCTRINAL first-mover result, its two controls, and the "
                "wording-fingerprint description that the de-boilerplating "
                "control rests on. Frozen before the recurring-formula "
                "programme, which may change how the fingerprints are "
                "understood but may not change these numbers.",
        "era": "DOCTRINAL_DIFFUSION_ERA_1",
        "frozenAt": "2026-08-31",
        "repositoryHead": head(),
        "unit": "(canonical non-statutory identity, code) pair, code-local",
        "codeHash": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()[:12]
                     for n in ("diffusion.py", "companions.py")},
        "eligibility": d["eligibility"],
        "typologyCodeLocal": d["phase3_typology"]["CODE"],
        "survivalCodeLocal": surv,
        "matched": d["phase7_matched"],
        "deBoilerplated": boil,
        "crossing": d["phase8_9_10_crossing"],
        "articleSourceOrder": d["phase11_12_articleSourceOrder"],
        "wordingFingerprints": d["phase17_templatePropagation"],
        "sourceMobility": d["phase20_sourceMobility"],
        "statuteVsDoctrine": d["phase21_statuteVsDoctrine"],
        "entrantForecastability": d["phase25_entrantForecastability"],
        "theOpenQuestion": "The de-boilerplating control removed every mention "
                           "whose +-90 character wording fingerprint recurs in "
                           "ten or more judgments. It is NOT established that "
                           "those fingerprints are boilerplate. A recurring "
                           "form of words may be the observable carrier of a "
                           "stable legal proposition, in which case the "
                           "control removed signal rather than noise. The "
                           "flip is a fact; its interpretation is not.",
        "whatWouldMoveThis": "New data, or a demonstration that the "
                             "fingerprint unit was mis-specified. Neither is "
                             "a reason to overwrite this file: a later era "
                             "gets its own.",
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
            print("the frozen doctrinal diffusion baseline has moved:")
            for k in moved:
                print(f"  {k}")
            return 1
        print("doctrinal diffusion baseline unchanged since it was frozen")
        return 0
    if OUT.exists():
        print(f"{OUT.name} already exists; a frozen baseline is not rewritten")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"froze the doctrinal diffusion baseline -> frozen/{OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
