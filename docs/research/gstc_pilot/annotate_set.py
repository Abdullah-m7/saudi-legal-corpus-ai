#!/usr/bin/env python3
"""Annotation workbench for any of the four labelled sets.

    python3 annotate_set.py sheet --set gstc_test --out <path>
    python3 annotate_set.py merge --set gstc_test --labels <path>

The held-out sets are opened through the same tool as the development ones so
that nothing about how they are read differs. What differs is the rule: a
held-out set is read once, labelled without reference to any prediction, and
scored once. `freeze.py --check` refuses to certify a test number reported
after the citation layer has moved.
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
from splits import FRAME, RAW, scrub           # noqa: E402

SETS = {
    "gstc_dev": HERE / "gstc_dev.json",
    "gstc_test": HERE / "gstc_test_frozen.json",
    "moj_dev": HERE / "moj_dev.json",
    "moj_test": HERE / "moj_test_frozen.json",
    "gstc_test2": HERE / "gstc_test2_frozen.json",
}
WIDE = 650


def texts_for(spec):
    if spec.get("source", "").startswith("MOJ"):
        from moj_splits import judgments
        want = set(spec["documents"])
        return {d["id"]: (d.get("text") or "")
                for d in judgments() if d["id"] in want}
    return {doc: (RAW / doc.replace(".pdf", ".txt")).read_text(
        encoding="utf-8", errors="ignore") for doc in spec["documents"]}


def sheet(path, out_path):
    spec = json.loads(path.read_text(encoding="utf-8"))
    raw = texts_for(spec)
    canon = {k: trace(v)[0] for k, v in raw.items()}
    frames = {k: [m.start() for m in FRAME.finditer(v)] for k, v in canon.items()}
    lines = []
    for item in spec["items"]:
        text = canon[item["doc"]]
        off = frames[item["doc"]][item["frameIndex"]]
        lo, hi = max(0, off - WIDE), min(len(text), off + WIDE)
        lines.append("=" * 78)
        lines.append(f"{item['id']}  {item['doc']}  token «{item['token']}»")
        lines.append("-" * 78)
        lines.append(scrub(text[lo:off]) + " ⟦" + item["token"] + "⟧ "
                     + scrub(text[off + len(item["token"]):hi]))
        lines.append("")
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(spec['items'])} items -> {out_path}")


def merge(path, labels_path):
    spec = json.loads(path.read_text(encoding="utf-8"))
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    by_id = {i["id"]: i for i in spec["items"]}
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
    spec["annotated"] = True
    spec["labelFields"] = list(FIELDS)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
    cited = sum(1 for i in spec["items"] if i["label"]["isCitation"])
    print(f"{len(spec['items'])} labelled, {cited} citations, "
          f"{len(spec['items']) - cited} non-citations")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("sheet", "merge"):
        sp = sub.add_parser(name)
        sp.add_argument("--set", choices=sorted(SETS), required=True)
        sp.add_argument("--out" if name == "sheet" else "--labels",
                        required=True)
    a = ap.parse_args()
    target = SETS[a.set]
    if a.cmd == "sheet":
        sheet(target, a.out)
    else:
        merge(target, a.labels)
