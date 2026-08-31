#!/usr/bin/env python3
"""Does "near" mean "about the same thing"?

The strongest evidence in the programme is a within-judgment contrast: in
2,137 judgments citing both, the Evidence Law's citations sit nearer
non-statutory authority than the Commercial Courts Law's in three quarters of
them. That claim rests entirely on a measurement decision -- that a fiqh
mention within N characters of a statutory citation is, in some legible sense,
part of the same piece of reasoning.

That decision was made by sensitivity analysis alone: three windows were
reported and the ones that agreed were relied on. Agreement between windows is
not the same as the windows measuring what they are supposed to. So this draws
the passages themselves and asks the only question that can settle it:

    is the non-statutory authority nearest this statutory citation part of
    the same reasoning proposition?  RELATED / UNRELATED / AMBIGUOUS

This is a construct check on a measurement unit, not a human gate on a result.
If the windows are mostly RELATED the unit is usable and the quantitative
finding stands on its own; if they are mostly UNRELATED the finding is an
artefact of proximity and has to be withdrawn.

    python3 locality_check.py sheet --out <path>
"""
import argparse
import collections
import gzip
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
from gold import scrub                # noqa: E402
from windows import judgments, year_of   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
DOCKET = HERE / "docket_layer.jsonl.gz"
OUT = HERE / "locality_gold.json"
NONSTATUTE = ("fiqh_source", "legal_maxim", "quran", "hadith",
              "judicial_principle", "custom")
PAIR = ("evidence_law", "commercial_courts_law")
SEED = 5501
N = 20


def candidates():
    """Judgments citing both codes of the contrast, with authority present."""
    out = []
    with gzip.open(DOCKET, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if "_schema" in r or r["y"] not in (1444, 1445, 1446):
                continue
            if set(PAIR) <= set(r["local"]) and r["courtNonStatuteMentions"]:
                out.append(r["j"])
    return out


def sheet(out_path):
    ids = candidates()
    rng = random.Random(SEED)
    ids.sort()
    rng.shuffle(ids)
    want = set(ids[:N])
    index, order = M.build(REGISTRY)
    lines = ["LOCALITY CONSTRUCT CHECK", "",
             "For each statutory citation below, the nearest non-statutory "
             "authority in the court's reasons is shown with the text between "
             "them. One question: is that authority part of the same reasoning "
             "proposition as the statutory citation?", ""]
    items = []
    for rec in judgments():
        if rec["id"] not in want or year_of(rec) not in (1444, 1445, 1446):
            continue
        text, s = rec["text"], rec.get("sections") or {}
        stat, non = [], []
        for m in A.mentions(text, s, index, order):
            if m.get("inQuote") or A.voice(m) != "court_reasoning":
                continue
            if m["type"] == "statute" and m.get("instrument") in PAIR:
                stat.append((m["at"], m["instrument"], m.get("article")))
            elif m["type"] in NONSTATUTE:
                non.append((m["at"], m["type"]))
        if not stat or not non:
            continue
        for at, inst, art in stat:
            q, qt = min(non, key=lambda x: abs(x[0] - at))
            d = q - at
            ident = f"L{len(items):03d}"
            lo, hi = (at, q) if d > 0 else (q, at)
            items.append({"id": ident, "judgment": rec["id"],
                          "instrument": inst, "article": art,
                          "authorityType": qt, "signedDistance": d,
                          "withinW500": abs(d) <= 500,
                          "withinW1000": abs(d) <= 1000})
            lines += ["=" * 78,
                      f"{ident}   {inst} art. {art}   nearest: {qt} at "
                      f"{d:+d} characters",
                      scrub(re.sub(r"\s+", " ",
                                   text[max(0, lo - 220):hi + 220])[:1400]),
                      ""]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")
    OUT.write_text(json.dumps(
        {"seed": SEED, "pair": list(PAIR), "judgmentsDrawn": len(want),
         "question": "is the nearest non-statutory authority part of the same "
                     "reasoning proposition as this statutory citation?",
         "labels": [], "items": items}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print(f"{len(items)} citation neighbourhoods from {len(want)} judgments "
          f"-> {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sheet"); p.add_argument("--out", required=True)
    a = ap.parse_args()
    sheet(a.out)
