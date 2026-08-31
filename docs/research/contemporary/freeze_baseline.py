#!/usr/bin/env python3
"""Freeze the AI-transition baseline, and refuse to rewrite it.

The point of a baseline is that it was written down before the thing it will
be compared against happened. A baseline that a later session can quietly
regenerate is not a baseline, it is a current reading. So this writes one
snapshot and refuses to overwrite it; `--check` says what has moved since.

    python3 freeze_baseline.py          # write, if absent
    python3 freeze_baseline.py --check  # compare the live baseline against it
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = HERE / "ai_baseline_results.json"
OUT = HERE / "frozen" / "ai_transition_baseline.json"


def flat(d, pre=""):
    out = {}
    for k, v in sorted(d.items()):
        p = f"{pre}.{k}" if pre else k
        if isinstance(v, dict):
            out.update(flat(v, p))
        elif isinstance(v, (int, float)):
            out[p] = v
    return out


def main():
    live = json.loads(LIVE.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        if not OUT.exists():
            print("no frozen baseline yet; run without --check")
            return 1
        old = json.loads(OUT.read_text(encoding="utf-8"))
        a, b = flat(old), flat(live)
        moved = [(k, a[k], b[k]) for k in sorted(a) if k in b and a[k] != b[k]]
        gone = sorted(set(a) - set(b))
        # provenance is not a number and must still be checked: a baseline
        # whose inputs changed underneath it is not the baseline any more
        oh, nh = old.get("dataHashes", {}), live.get("dataHashes", {})
        moved += [(f"dataHashes.{k}", oh[k], nh.get(k, "ABSENT"))
                  for k in sorted(oh) if oh[k] != nh.get(k)]
        if not moved and not gone:
            print(f"the AI-transition baseline is unchanged "
                  f"({len(a)} numeric fields, cutoff {old['dataCutoff']})")
            return 0
        print(f"{len(moved)} field(s) moved since the baseline was frozen "
              f"at {old['dataCutoff']}:")
        for k, x, y in moved[:40]:
            print(f"  {k}: {x} -> {y}")
        for k in gone[:10]:
            print(f"  {k}: no longer produced")
        return 1
    if OUT.exists():
        print(f"{OUT.name} already exists and is not rewritten. "
              f"Delete it deliberately, or use --check.")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(live, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"froze {len(flat(live))} numeric fields at cutoff "
          f"{live['dataCutoff']} -> {OUT.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
