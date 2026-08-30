#!/usr/bin/env python3
"""Re-run the project's own claims against the hand-labelled gold.

The published measurements count every citation a pattern finds anywhere in a
judgment. The gold sets say who was speaking. This asks what the difference
does to the claims that have already been made, and reports the answer
whichever way it comes out.

    python3 claims_audit.py           # table
    python3 claims_audit.py --json    # claims_audit.json
"""

import collections
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The procedural set as the applied-law measurement defines it, by the names
# the gold records rather than by registry key, so that this file can be read
# against the labels without loading the registry.
PROCEDURAL = {
    "نظام المرافعات الشرعية", "الالئحة التنفيذية لنظام المرافعات الشرعية",
    "نظام المحاكم التجارية", "الالئحة التنفيذية لنظام المحاكم التجارية",
    "نظام المحكمة التجارية", "نظام الإثبات", "الأدلة الإجرائية لنظام الإثبات",
    "نظام التحكيم", "الالئحة التنفيذية لنظام التحكيم", "نظام المحاماة",
    "نظام الإفلاس", "لائحة المعلومات والوثائق", "نظام القضاء",
    "الالئحة التنفيذية لإجراءات الاستئناف", "نظام التنفيذ",
    "الالئحة التنفيذية لنظام التنفيذ",
}
SETS = {"MOJ": ("moj_dev.json", "moj_test_frozen.json"),
        "GSTC": ("gstc_dev.json", "gstc_test_frozen.json")}


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(100 * max(0.0, centre - half), 1),
            round(100 * min(1.0, centre + half), 1))


def audit():
    out = {}
    for name, files in SETS.items():
        labels = []
        for f in files:
            labels += [i["label"]
                       for i in json.loads((HERE / f).read_text(
                           encoding="utf-8"))["items"]]
        cited = [l for l in labels if l["isCitation"]]
        n = len(cited)
        seg = collections.Counter(l["segment"] for l in cited)
        own = seg.get("reasoning", 0)
        with_inst = [l for l in cited if l["instrument"]]
        reasoning = [l for l in with_inst if l["segment"] == "reasoning"]

        def share(rows):
            k = sum(1 for l in rows if l["instrument"] in PROCEDURAL)
            lo, hi = wilson(k, len(rows))
            return {"procedural": k, "of": len(rows),
                    "pct": round(100 * k / len(rows), 1) if rows else None,
                    "ci95": [lo, hi]}

        out[name] = {
            "sampled": len(labels),
            "citations": n,
            "segments": {k: {"n": v, "pct": round(100 * v / n, 1),
                             "ci95": list(wilson(v, n))}
                         for k, v in seg.most_common()},
            "tribunalOwnShare": {"n": own, "pct": round(100 * own / n, 1),
                                 "ci95": list(wilson(own, n))},
            "overcountFactor": round(n / own, 2) if own else None,
            "proceduralShareAllCitations": share(with_inst),
            "proceduralShareReasoningOnly": share(reasoning),
        }
    return out


if __name__ == "__main__":
    a = audit()
    if "--json" in sys.argv:
        (HERE / "claims_audit.json").write_text(
            json.dumps(a, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(json.dumps(a, ensure_ascii=False, indent=1))
    else:
        for name, d in a.items():
            print(f"\n{name}: {d['citations']} citations of {d['sampled']} sampled")
            for k, v in d["segments"].items():
                print(f"  {k:12} {v['n']:4d}  {v['pct']:5.1f}%  {v['ci95']}")
            t = d["tribunalOwnShare"]
            print(f"  tribunal's own: {t['pct']}% {t['ci95']}, "
                  f"over-count factor {d['overcountFactor']}x")
            for key, title in (("proceduralShareAllCitations", "all citations"),
                               ("proceduralShareReasoningOnly", "reasoning only")):
                s = d[key]
                print(f"  procedural share, {title:14} "
                      f"{s['procedural']}/{s['of']} = {s['pct']}% {s['ci95']}")
