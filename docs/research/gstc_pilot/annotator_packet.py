#!/usr/bin/env python3
"""A blinded packet for a second annotator, and nothing that pretends to be one.

The brief's rule: if no second person is actually available, do not invent an
agreement figure, and do not run a second model and call it inter-annotator
agreement. So this builds the packet and stops. The worksheet is written to the
scratchpad, never to the repository, for the same reason `annotate.py` writes
its wide view there: a 1300-character window is a larger republication of a
text whose redaction the publisher already got wrong.

What lives in the repository is the *design*: which items, why those, the
protocol the second reader is to follow, and an empty labels file. That is
enough for anyone to reproduce the packet and to check afterwards that the
sample was fixed before the second reading, not after.

Stratified across the five things the first reading found hard, so that an
agreement figure computed later is informative about those and not about the
easy majority:

  source              MOJ judgments vs GSTC digests
  citation            citation vs non-citation
  paragraph           carries a paragraph vs does not
  instrument          resolvable locally vs by anaphora/carry vs not at all
  segment             the tribunal's own voice vs a party's plea

    python3 annotator_packet.py --out <dir>
"""
import argparse, collections, json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "canon"))
from canonical import trace                       # noqa: E402
from splits import FRAME, RAW, scrub              # noqa: E402
from evaluate import documents_for                # noqa: E402

SEED = 7
TARGET = 80
SETS = ["gstc_test2_frozen.json", "moj_test_frozen.json",
        "gstc_test_frozen.json", "moj_dev.json"]
WIDE = 650


def cell(item):
    g = item["label"]
    src = "MOJ" if item["id"].startswith("moj") else "GSTC"
    if not g["isCitation"]:
        return (src, "non-citation")
    if g["instrumentSource"] in (None, "absent"):
        return (src, "citation, instrument absent")
    if g["instrumentSource"] != "local":
        return (src, "citation, instrument by anaphora or carry")
    if g["segment"] == "party":
        return (src, "citation, party plea")
    if g["paragraph"]:
        return (src, "citation, with paragraph")
    return (src, "citation, plain")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    pool = collections.defaultdict(list)
    specs = {}
    for name in SETS:
        path = HERE / name
        if not path.exists():
            continue
        spec = json.loads(path.read_text(encoding="utf-8"))
        specs[name] = spec
        for item in spec["items"]:
            if item.get("label"):
                pool[cell(item)].append((name, item))

    rng = random.Random(SEED)
    cells = sorted(pool)
    per = max(1, TARGET // len(cells))
    chosen = []
    for c in cells:
        items = sorted(pool[c], key=lambda p: p[1]["id"])
        rng.shuffle(items)
        chosen += [(c,) + p for p in items[:per]]
    rng.shuffle(chosen)

    # the worksheet: context only. No gold, no prediction, no stratum label.
    texts = {}
    for name, spec in specs.items():
        for doc, raw in documents_for(spec).items():
            texts.setdefault(doc, trace(raw)[0])
    frames = {k: [m.start() for m in FRAME.finditer(v)] for k, v in texts.items()}

    lines, index = [], []
    for n, (c, setname, item) in enumerate(chosen):
        text = texts[item["doc"]]
        off = frames[item["doc"]][item["frameIndex"]]
        lo, hi = max(0, off - WIDE), min(len(text), off + WIDE)
        tag = f"A{n:03d}"
        index.append({"packetId": tag, "set": setname, "id": item["id"],
                      "stratum": " / ".join(c)})
        lines += ["=" * 78,
                  f"{tag}   token «{item['token']}»", "-" * 78,
                  scrub(text[lo:off]) + " ⟦" + item["token"] + "⟧ "
                  + scrub(text[off + len(item['token']):hi]), ""]
    (Path(a.out) / "worksheet.txt").write_text("\n".join(lines), encoding="utf-8")

    (HERE / "annotator_packet.json").write_text(json.dumps(
        {"seed": SEED, "wideWindow": WIDE, "items": index,
         "status": "OPEN_FOR_HUMAN",
         "note": "No second annotator has read this packet. No agreement "
                 "figure exists and none is claimed."},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    template = {i["packetId"]: {f: None for f in
                ("isCitation", "articleForm", "articleNumber", "paragraph",
                 "instrument", "instrumentSource", "segment", "notes")}
                for i in index}
    (Path(a.out) / "labels_template.json").write_text(
        json.dumps(template, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(chosen)} items over {len(cells)} strata -> {a.out}/worksheet.txt")
    for c in cells:
        print(f"  {' / '.join(c):48} available {len(pool[c]):4}  drawn {per}")


if __name__ == "__main__":
    main()
