#!/usr/bin/env python3
"""Annotation workbench for MOJ_DEV, in the same schema as the GSTC one.

    python3 moj_annotate.py sheet  --out <path>
    python3 moj_annotate.py merge  --labels <path>
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import trace                    # noqa: E402
from annotate import FIELDS                    # noqa: E402
from moj_splits import judgments               # noqa: E402
from splits import scrub                       # noqa: E402

DEV = HERE / "moj_dev.json"
WIDE = 650


def texts_for(ids):
    want = set(ids)
    out = {}
    for d in judgments():
        if d["id"] in want:
            out[d["id"]] = d.get("text") or ""
            if len(out) == len(want):
                break
    return out


def sheet(out_path):
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    raw = texts_for({i["doc"] for i in dev["items"]})
    canon = {k: trace(v)[0] for k, v in raw.items()}
    lines = []
    for item in dev["items"]:
        text = canon[item["doc"]]
        # locate by frameIndex under the full canonicalisation
        from splits import FRAME
        import re as _re
        starts = [m.start() for m in FRAME.finditer(text)]
        off = starts[item["frameIndex"]]
        lo, hi = max(0, off - WIDE), min(len(text), off + WIDE)
        lines.append("=" * 78)
        lines.append(f"{item['id']}  {item['doc']}  token «{item['token']}»")
        lines.append("-" * 78)
        lines.append(scrub(text[lo:off]) + " ⟦" + item["token"] + "⟧ "
                     + scrub(text[off + len(item["token"]):hi]))
        lines.append("")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(dev['items'])} items -> {out_path}")


def merge(labels_path):
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    by_id = {i["id"]: i for i in dev["items"]}
    unknown = sorted(set(labels) - set(by_id))
    if unknown:
        sys.exit(f"unknown ids: {unknown[:5]}")
    missing = sorted(set(by_id) - set(labels))
    if missing:
        sys.exit(f"{len(missing)} items unlabelled, first: {missing[:5]}")
    for ident, label in labels.items():
        extra = sorted(set(label) - set(FIELDS))
        if extra:
            sys.exit(f"{ident}: unknown fields {extra}")
        by_id[ident]["label"] = {f: label.get(f) for f in FIELDS}
    dev["annotated"] = True
    dev["labelFields"] = list(FIELDS)
    DEV.write_text(json.dumps(dev, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    cited = sum(1 for i in dev["items"] if i["label"]["isCitation"])
    print(f"{len(dev['items'])} labelled, {cited} citations, "
          f"{len(dev['items']) - cited} non-citations")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("--out", required=True)
    m = sub.add_parser("merge"); m.add_argument("--labels", required=True)
    a = ap.parse_args()
    sheet(a.out) if a.cmd == "sheet" else merge(a.labels)
