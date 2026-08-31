#!/usr/bin/env python3
"""The reusable layer: one row per authority mention, not per judgment.

`export.py` writes judgment-level counts. That answers "how often" and cannot
answer "which article, invoked by whom, in what role". This writes the layer
underneath it, so every later question in this repository is a scan of a 30 MB
file rather than a four-hour pass over 44,144 judgments.

One row per mention. **No judgment text.** The row carries what the mention
is, who made it and where, and nothing from which the sentence could be
reconstructed:

    j        judgment id, as the publisher issues it
    y        Hijri year
    ct       court type
    role     court_reasoning | party_argument | recital | operative | unknown
    spec     which speaker specification admits it: S (strict only, i.e. a
             cue-based party attribution), W (wide only, i.e. a recital
             mention with no cue), B (both, or not a party mention at all)
    t        authority type, one of nine
    r        rule id that fired -- the audit trail back to authority.py
    q        1 if the mention sits inside a passage the judgment is quoting
    inst     registry track id, statute mentions only
    art      article number, normalised across «١٦» «16» «السادسة عشرة»
    proc     1 procedural, 0 substantive, absent where not validated
    res      how the instrument was resolved: named | anaphoric | absent

`res` is the confidence field. An anaphorically resolved instrument is a
weaker observation than a named one and a later user should be able to drop
it without re-parsing anything.

    python3 layer.py [--out <path>] [--view contemporary_5y]
"""
import argparse
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "arabic_paper"))
import arabic_ordinals as AO          # noqa: E402
import authority as A                 # noqa: E402
import match_instruments as M         # noqa: E402
from claim import side                # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
DEFAULT = HERE / "authority_mentions.jsonl.gz"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT))
    ap.add_argument("--view", default="contemporary_5y")
    args = ap.parse_args()
    years = set(VIEWS[args.view])
    index, order = M.build(REGISTRY)
    n = docs = 0
    with gzip.open(args.out, "wt", encoding="utf-8") as fh:
        fh.write(json.dumps({"_schema": {
            "view": args.view, "years": sorted(years),
            "fields": "j y ct role spec t r q inst art proc res",
            "spec": "S=strict-only party, W=wide-only party, B=both/not-party",
            "res": "named | anaphoric | absent",
            "note": "no judgment text; counts and identifiers only"},
        }, ensure_ascii=False) + "\n")
        for rec in judgments():
            y = year_of(rec)
            if y not in years:
                continue
            docs += 1
            text, sections = rec["text"], rec.get("sections") or {}
            for m in A.mentions(text, sections, index, order):
                s_side, w_side = side(m, "strict"), side(m, "wide")
                spec = ("B" if s_side == w_side else
                        "S" if s_side == "party" else "W")
                row = {"j": rec["id"], "y": y,
                       "ct": rec.get("court_type") or "",
                       "role": A.voice(m), "spec": spec,
                       "t": m["type"], "r": m["rule"],
                       "q": 1 if m.get("inQuote") else 0}
                if m["type"] == "statute":
                    row["res"] = (m["instrumentNamed"] or "absent")
                    if m["instrument"]:
                        row["inst"] = m["instrument"]
                        num, _ = AO.parse(m["article"] or "")
                        if num is not None:
                            row["art"] = num
                    if m["procedural"] is not None:
                        row["proc"] = 1 if m["procedural"] else 0
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                n += 1
    size = Path(args.out).stat().st_size
    print(f"{n:,} mentions from {docs:,} judgments -> {args.out}"
          f"  ({size/1e6:.1f} MB gzipped)")


if __name__ == "__main__":
    main()
