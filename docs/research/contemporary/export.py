#!/usr/bin/env python3
"""The reusable layer: speaker-aware authority annotations, per judgment.

Everything in this directory computes aggregates. This writes the layer those
aggregates were computed from, so the next question does not need another full
pass over the corpus, and so someone else can ask a question this project did
not.

One row per judgment. **No judgment text is written.** The row carries the
judgment id, its year and court, and counts — nothing from which the text
could be reconstructed, and nothing the publisher had not already redacted.

    judgment            the publisher's own opaque id
    year, court, type   as published
    reasoned            does it carry «الأسباب» → «حكمت الدائرة»
    court_<type>        mentions in the bench's own reasons, by authority type
    partyS_<type>       party mentions, STRICT specification (cue-based)
    partyW_<type>       party mentions, WIDE specification (whole recital)
    quoted              mentions inside passages the judgment is quoting
    shape               hybrid | statute_only | non_statute_only | none
    coreArticles        the (instrument, article) pairs the BENCH cited,
                        normalised, as a compact string

Written as JSONL, gzipped, so it can be streamed.

    python3 export.py [--out <path>]
"""
import argparse
import collections
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
import voice_attribution as V         # noqa: E402
from claim import side, NONSTATUTE    # noqa: E402
from windows import judgments, year_of, VIEWS   # noqa: E402

REGISTRY = HERE.parents[2] / "data" / "corpus_registry" / "corpus_registry.json"
DEFAULT = HERE / "authority_layer.jsonl.gz"
YEARS = set(VIEWS["contemporary_5y"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT))
    args = ap.parse_args()
    index, order = M.build(REGISTRY)
    n = 0
    with gzip.open(args.out, "wt", encoding="utf-8") as fh:
        for rec in judgments():
            y = year_of(rec)
            if y not in YEARS:
                continue
            text, sections = rec["text"], rec.get("sections") or {}
            ms = A.mentions(text, sections, index, order)
            reasoned = any(v == "reasoning"
                           for _, _, v in V.segments(text, sections))
            court = collections.Counter()
            ps = collections.Counter()
            pw = collections.Counter()
            quoted = 0
            arts = set()
            for m in ms:
                if m.get("inQuote"):
                    quoted += 1
                    continue
                if A.voice(m) == "court_reasoning":
                    court[m["type"]] += 1
                    if m["type"] == "statute" and m["instrument"]:
                        num, _ = AO.parse(m["article"] or "")
                        if num is not None:
                            arts.add(f"{m['instrument']}:{num}")
                if side(m, "strict") == "party":
                    ps[m["type"]] += 1
                if side(m, "wide") == "party":
                    pw[m["type"]] += 1
            has_stat = court["statute"] > 0
            has_non = any(court[t] for t in NONSTATUTE)
            row = {
                "judgment": rec["id"], "year": y,
                "court": (rec.get("court") or "").strip(),
                "courtType": rec.get("court_type") or "",
                "reasoned": bool(reasoned), "quoted": quoted,
                "shape": ("hybrid" if has_stat and has_non else
                          "statute_only" if has_stat else
                          "non_statute_only" if has_non else "none")
                if reasoned else None,
            }
            for t in A.TYPES:
                if court[t]:
                    row[f"court_{t}"] = court[t]
                if ps[t]:
                    row[f"partyS_{t}"] = ps[t]
                if pw[t]:
                    row[f"partyW_{t}"] = pw[t]
            if arts:
                row["coreArticles"] = sorted(arts)
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    size = Path(args.out).stat().st_size
    print(f"{n:,} judgments -> {args.out}  ({size/1e6:.1f} MB gzipped)")
    print("no judgment text is written; counts and ids only")


if __name__ == "__main__":
    main()
