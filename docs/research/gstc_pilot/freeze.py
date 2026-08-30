#!/usr/bin/env python3
"""Record exactly which code a held-out evaluation was run with.

A frozen test set is only frozen if the thing measured against it is fixed
too. This writes the commit and the content hash of every file the citation
layer consists of, so a later reader can tell whether a reported test number
belongs to the code in front of them or to something since edited.

    python3 freeze.py            # write frozen.json
    python3 freeze.py --check    # fail if the code has moved since
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "frozen.json"

# Two groups, because they fail differently.
#
# PARSER is what decides an answer. If any of it moves, a held-out number
# reported afterwards is not a held-out number, and --check says so.
#
# HARNESS is what decides which questions are asked and how the answers are
# counted. Registering a new labelled set changes it; scoring logic changes it
# too. Both are recorded, and a change here is reported rather than fatal --
# but it has to be read, because a change to how a stage is *scored* is as
# capable of manufacturing a result as a change to the parser is.
PARSER = [
    "docs/research/canon/canonical.py",
    "docs/research/citation/numerals.py",
    "docs/research/citation/instruments.py",
    "docs/research/citation/grammar.py",
]
HARNESS = [
    "docs/research/gstc_pilot/evaluate.py",
    "docs/research/gstc_pilot/splits.py",
    "docs/research/gstc_pilot/moj_splits.py",
    "docs/research/gstc_pilot/gstc_test2.py",
]
FILES = PARSER + HARNESS


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def state():
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True,
                                check=True).stdout.strip()
    except Exception:
        commit = None
    return {"commit": commit,
            "parser": {path: digest(path) for path in PARSER},
            "harness": {path: digest(path) for path in HARNESS},
            "files": {path: digest(path) for path in FILES}}


if __name__ == "__main__":
    now = state()
    if "--check" in sys.argv:
        if not OUT.exists():
            sys.exit("no frozen.json: nothing has been frozen")
        was = json.loads(OUT.read_text(encoding="utf-8"))
        parser_was = was.get("parser") or was.get("files", {})
        moved = [p for p, h in parser_was.items()
                 if p in now["parser"] and now["parser"][p] != h]
        if moved:
            sys.exit("the PARSER has moved since the freeze:\n  "
                     + "\n  ".join(moved)
                     + "\n\nA test number reported after this is not a test "
                       "number. Re-freeze, and say in the write-up that the "
                       "held-out set was opened twice.")
        drifted = [p for p, h in (was.get("harness") or {}).items()
                   if now["harness"].get(p) != h]
        print(f"parser unchanged since {was['commit'][:12]}")
        if drifted:
            print("harness changed (read the diff before trusting a number):")
            for p in drifted:
                print("  " + p)
    else:
        OUT.write_text(json.dumps(now, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
        print(f"frozen at {now['commit'][:12]}")
        for group in ("parser", "harness"):
            print(f"  [{group}]")
            for path, h in now[group].items():
                print(f"    {h[:12]}  {path}")
