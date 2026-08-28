#!/usr/bin/env python3
"""Refuse to typeset a result that predates the code which produced it.

check_numbers.py stops a figure being typed by hand. It cannot stop the other
way a manuscript goes wrong, which is subtler and was found in this project by
reading rather than by any guard: the figure is generated, the generator reads
a JSON, and the JSON was written before the extractor underneath it was fixed.
Every check passes and the paper still reports superseded numbers.

That happened here. The pattern that finds a statutory citation was missing a
class of Arabic prefixes and was corrected; two analyses were not re-run
afterwards, and paper 9 typeset their output for a week. Re-running them moved
the pooled comparison it reported, and the paired test added at the same time
reversed its sign.

So: for each `<name>_results.json`, find the script that writes it, follow that
script's local imports transitively, and hash those sources. A stamp file
records the hash each result was last generated against. If the code has moved
since, the result is stale and the guard says which file to re-run.

    python3 check_fresh.py            # check
    python3 check_fresh.py --stamp    # record the current state as current

Hashing the sources, rather than comparing mtimes or reading git history, is
the third design and the first correct one. Mtimes are rewritten wholesale by
`git checkout`, so the mtime version reported eleven current files as stale
after an ordinary branch switch --- and a guard that cries wolf teaches its
author to ignore it. Git history is checkout-proof but cannot see a re-run
that produced byte-identical output, which is exactly what a re-run after a
harmless refactor produces: it reported a file as stale that had been
regenerated and verified an hour earlier. A hash of the code answers the
question actually being asked --- is this result the output of *this* code ---
and answers it the same way in a working tree, a fresh clone, or a zip file.

Stamp only after re-running. The stamp is a claim that the results on disk
came from the code on disk, and it is committed, so it is a claim to everyone
who clones the repository.
"""

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "arabic_paper"
STAMP = SRC / "freshness.json"

# reversal_model.py writes reversal_model_results.json and, run with a window,
# reversal_model_1439_1444_results.json. The producer is the longest script
# name that prefixes the JSON name.
SUFFIX = re.compile(r"_results\.json$")


def producer(results):
    stem = SUFFIX.sub("", results.name)
    while stem:
        candidate = SRC / f"{stem}.py"
        if candidate.exists():
            return candidate
        stem = stem.rpartition("_")[0]
    return None


def local_imports(script, seen=None):
    """The script, plus every module in this directory it imports, recursively."""
    seen = seen if seen is not None else set()
    if script in seen:
        return seen
    seen.add(script)
    try:
        tree = ast.parse(script.read_text(encoding="utf-8"))
    except (SyntaxError, OSError):
        return seen
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    for name in names:
        child = SRC / f"{name.split('.')[0]}.py"
        if child.exists():
            local_imports(child, seen)
    return seen


def code_hash(script):
    """One digest over every source file this result depends on."""
    h = hashlib.sha256()
    for dep in sorted(local_imports(script), key=lambda p: p.name):
        h.update(dep.name.encode())
        h.update(hashlib.sha256(dep.read_bytes()).digest())
    return h.hexdigest()


def survey():
    out = {}
    for results in sorted(SRC.glob("*_results.json")):
        script = producer(results)
        if script is not None:
            out[results.name] = code_hash(script)
    return out


def main():
    now = survey()
    if "--stamp" in sys.argv:
        STAMP.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
        print(f"stamped {len(now)} result files as current with their code")
        return 0
    if not STAMP.exists():
        print("no freshness.json --- run with --stamp after a full re-run")
        return 1
    was = json.loads(STAMP.read_text(encoding="utf-8"))
    stale = [name for name, h in now.items() if was.get(name) != h]
    if stale:
        print(f"{len(stale)} result file(s) no longer match the code that "
              f"writes them --- re-run, then --stamp:")
        for name in stale:
            script = producer(SRC / name)
            deps = ", ".join(sorted(d.name for d in local_imports(script)))
            print(f"  {name}\n    depends on: {deps}")
        return 1
    gone = sorted(set(was) - set(now))
    for name in gone:
        print(f"  ? {name} is stamped but no longer present")
    print(f"all {len(now)} result files are current with their code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
