#!/usr/bin/env python3
"""Do the headline shares survive dropping duplicate judgments?

The portal serves some judgments twice, and the article says so. Saying so is
not enough: the busiest articles are cited in standard formulas, and standard
formulas are exactly what a duplicated judgment repeats, so a reader is
entitled to ask whether the concentration is partly an artefact of the
duplication. This recomputes the instrument-level and article-level shares
over distinct texts only — first occurrence kept, later identical copies
dropped — and prints both sets side by side.
"""

import collections
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

import arabic_ordinals as A       # noqa: E402
import match_instruments as M     # noqa: E402
import voice_attribution as V     # noqa: E402

REGISTRY = REPO / "data" / "corpus_registry" / "corpus_registry.json"


def run(skip_duplicates):
    index, order = M.build(REGISTRY)
    inst = collections.Counter()
    arts = collections.Counter()
    seen = set()
    kept = 0
    for shard in sorted((HERE / "judgments").glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            text = r["text"]
            if skip_duplicates:
                h = hashlib.sha1(" ".join(text.split()).encode("utf-8")).digest()
                if h in seen:
                    continue
                seen.add(h)
            kept += 1
            last = M.Recent()
            for m in V.CITE.finditer(text):
                tid, kind = M.match(m.group(2), index, order, last)
                if kind == "named":
                    last.note(tid)
                if not tid:
                    continue
                inst[tid] += 1
                num, _ = A.parse(m.group(1))
                if num is not None:
                    arts[(tid, num)] += 1
    return kept, inst, arts


def report(label, kept, inst, arts):
    ti, ta = sum(inst.values()), sum(arts.values())
    ri = sorted(inst.values(), reverse=True)
    ra = sorted(arts.values(), reverse=True)
    proc = sum(v for k, v in inst.items() if k in M.PROCEDURAL)
    print(f"{label:<22}{kept:>9,}{ti:>11,}{100*ri[0]/ti:>9.1f}"
          f"{100*sum(ri[:10])/ti:>9.1f}{100*proc/ti:>12.1f}"
          f"{100*ra[0]/ta:>10.1f}{100*sum(ra[:10])/ta:>9.1f}")


def main():
    print(f"{'corpus':<22}{'judgments':>9}{'citations':>11}{'top-1':>9}"
          f"{'top-10':>9}{'procedural':>12}{'art top-1':>10}{'top-10':>9}")
    a = run(False)
    report("as published", *a)
    b = run(True)
    report("distinct texts only", *b)

    out = {}
    for label, (kept, inst, art) in (("as_published", a), ("distinct", b)):
        ti, ta = sum(inst.values()), sum(art.values())
        ri, ra = sorted(inst.values(), reverse=True), sorted(art.values(), reverse=True)
        out[label] = {
            "judgments": kept, "citations": ti,
            "top1": 100 * ri[0] / ti, "top10": 100 * sum(ri[:10]) / ti,
            "procedural": 100 * sum(v for k, v in inst.items()
                                    if k in M.PROCEDURAL) / ti,
            "article_top1": 100 * ra[0] / ta,
            "article_top10": 100 * sum(ra[:10]) / ta,
        }
    (HERE / "dedup_robustness_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote dedup_robustness_results.json")


if __name__ == "__main__":
    main()
