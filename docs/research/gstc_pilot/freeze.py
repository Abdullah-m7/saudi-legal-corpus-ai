#!/usr/bin/env python3
"""Record exactly which code a held-out evaluation was run with.

A frozen test set is only frozen if the thing measured against it is fixed
too. This writes the commit and the content hash of every file the citation
layer consists of, so a later reader can tell whether a reported test number
belongs to the code in front of them or to something since edited.

A freeze is also a version. When a defect is found *after* a held-out set has
been opened, the honest response is not to re-open the set: the number that
was reported belongs to the code that produced it and stays attached to it.
So freezing archives the record it replaces under frozen_history/, and the
write-ups name the version each held-out number belongs to.

    python3 freeze.py            # write frozen.json, archiving the old one
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
HISTORY = HERE / "frozen_history"

# v1  the citation layer as it stood when GSTC_TEST_FROZEN, MOJ_TEST_FROZEN
#     and GSTC_TEST2_FROZEN were opened. Every held-out number this project
#     reports belongs to v1 and is not restated for v2.
# v2  adds two representation repairs found afterwards, by reading whole
#     judgments and a candidate third source: Arabic Presentation Forms, and
#     Arabic combining marks on the head noun. Neither is a matching rule;
#     both are the text arriving as something other than the characters it
#     renders as. No held-out set was re-opened to validate them.
VERSION = "v2"

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
    # added in v2. It was always a parser file -- CITE decides what counts as
    # a citation for every corpus analysis -- and was recorded in neither
    # group, which is exactly the omission a freeze exists to prevent.
    "docs/research/arabic_paper/voice_attribution.py",
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
    return {"version": VERSION,
            "commit": commit,
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
        print(f"parser unchanged since {was['commit'][:12]} "
              f"({was.get('version', 'v1')})")
        if drifted:
            print("harness changed (read the diff before trusting a number):")
            for p in drifted:
                print("  " + p)
    else:
        if OUT.exists():
            old = json.loads(OUT.read_text(encoding="utf-8"))
            HISTORY.mkdir(exist_ok=True)
            name = f"{old.get('version', 'v1')}-{(old.get('commit') or '')[:12]}.json"
            (HISTORY / name).write_text(
                json.dumps(old, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8")
            print(f"archived the previous freeze as frozen_history/{name}")
        OUT.write_text(json.dumps(now, ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
        print(f"frozen at {now['commit'][:12]} as {VERSION}")
        for group in ("parser", "harness"):
            print(f"  [{group}]")
            for path, h in now[group].items():
                print(f"    {h[:12]}  {path}")
