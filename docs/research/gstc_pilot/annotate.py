#!/usr/bin/env python3
"""Annotation workbench for GSTC_DEV.

Two subcommands, deliberately separated:

  sheet   writes a wide-context reading view outside the repository, because
          a 110-character window is enough to see an article number but not
          enough to resolve which instrument it belongs to. Instrument
          resolution is the thing that scored 0.0 per cent, so the annotator
          must be given what the parser would have to find.

  merge   folds a labels file back into gstc_dev.json, refusing any label
          whose id is unknown and any item left unlabelled.

The wide view is masked with the same masks the split used and is written to
the scratchpad, never to the repository: a wider window is a larger
republication of a text whose redaction the publisher already got wrong.

    python3 annotate.py sheet  --out <path>
    python3 annotate.py merge  --labels <path>
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "canon"))
sys.path.insert(0, str(HERE))
from canonical import canonicalise            # noqa: E402
from splits import RAW, scrub                  # noqa: E402

DEV = HERE / "gstc_dev.json"
WIDE = 700

FIELDS = ("isCitation", "articleForm", "articleNumber", "paragraph",
          "instrument", "instrumentSource", "segment", "notes")

# instrumentSource: how the instrument becomes recoverable at this occurrence
#   local          named in the same «من X» attachment
#   list_trailing  named once at the end of a coordinated list of articles and
#                  distributing backwards over its earlier members
#   anaphora       «هذه اللائحة», «النظام المذكور», «لائحته التنفيذية»
#   heading        recoverable only from a heading or the authorities block
#   absent         not recoverable from the document at all
#
# segment: whose citation this is. A pipeline that cannot tell these apart
#   cannot support any sentence of the form "the tribunal cited X".
#   reasoning | party | authorities | quotation | disposition | summary


def sheet(out):
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    cache = {}
    lines = []
    for item in dev["items"]:
        doc = item["doc"]
        if doc not in cache:
            src = (RAW / doc.replace(".pdf", ".txt")).read_text(
                encoding="utf-8", errors="ignore")
            cache[doc] = canonicalise(src)["canonical"]
        text = cache[doc]
        off = item["offset"]
        lo, hi = max(0, off - WIDE), min(len(text), off + WIDE)
        lines.append("=" * 78)
        lines.append(f"{item['id']}  {doc}  offset {off}  token «{item['token']}»")
        lines.append("-" * 78)
        lines.append(scrub(text[lo:off]) + " ⟦" + scrub(text[off:off + len(item["token"])])
                     + "⟧ " + scrub(text[off + len(item["token"]):hi]))
        lines.append("")
    Path(out).write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(dev['items'])} items -> {out}")


def merge(labels_path):
    dev = json.loads(DEV.read_text(encoding="utf-8"))
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in dev["items"]}
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
        if "isCitation" not in label:
            sys.exit(f"{ident}: isCitation is required")
        by_id[ident]["label"] = {f: label.get(f) for f in FIELDS}
    dev["annotated"] = True
    dev["labelFields"] = list(FIELDS)
    DEV.write_text(json.dumps(dev, ensure_ascii=False, indent=2) + "\n",
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
    if a.cmd == "sheet":
        sheet(a.out)
    else:
        merge(a.labels)
